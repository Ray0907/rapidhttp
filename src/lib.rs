use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use pyo3::exceptions::{PyException, PyValueError, PyRuntimeError};
use reqwest::blocking::Client as BlockingClient;
use std::collections::HashMap;
use std::time::Duration;
use bytes::Bytes;

// Custom exception types
pyo3::create_exception!(rapidhttp, HTTPError, PyException);
pyo3::create_exception!(rapidhttp, ConnectionError, PyException);
pyo3::create_exception!(rapidhttp, Timeout, PyException);
pyo3::create_exception!(rapidhttp, ConnectTimeout, Timeout);
pyo3::create_exception!(rapidhttp, ReadTimeout, Timeout);
pyo3::create_exception!(rapidhttp, TooManyRedirects, PyException);
pyo3::create_exception!(rapidhttp, RequestException, PyException);
pyo3::create_exception!(rapidhttp, URLRequired, PyException);
pyo3::create_exception!(rapidhttp, JSONDecodeError, PyException);

/// Create a client with redirect policy
fn create_client_with_redirects(allow_redirects: bool) -> PyResult<BlockingClient> {
    let mut builder = BlockingClient::builder()
        .pool_max_idle_per_host(100)
        .pool_idle_timeout(Some(Duration::from_secs(90)))
        .timeout(Duration::from_secs(30));
    
    if !allow_redirects {
        builder = builder.redirect(reqwest::redirect::Policy::none());
    }
    
    builder.build()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to create client: {}", e)))
}

/// Core HTTP client wrapper
#[pyclass]
struct Client {
    client: BlockingClient,
}

#[pymethods]
impl Client {
    #[new]
    fn new() -> PyResult<Self> {
        let client = BlockingClient::builder()
            .pool_max_idle_per_host(100)
            .pool_idle_timeout(Some(Duration::from_secs(90)))
            .timeout(Duration::from_secs(30))
            .build()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create client: {}", e)))?;
        
        Ok(Client { client })
    }

    fn request(
        &self,
        py: Python,
        method: String,
        url: String,
        params: Option<&PyDict>,
        headers: Option<&PyDict>,
        data: Option<&PyAny>,
        json: Option<&PyAny>,
        timeout: Option<f64>,
        allow_redirects: Option<bool>,
        verify: Option<bool>,
    ) -> PyResult<Response> {
        let method_str = method.to_uppercase();
        let method = reqwest::Method::from_bytes(method_str.as_bytes())
            .map_err(|e| PyValueError::new_err(format!("Invalid HTTP method: {}", e)))?;

        let mut request_builder = self.client.request(method.clone(), &url);

        // Add query parameters
        if let Some(params_dict) = params {
            let mut query_params = Vec::new();
            for (key, value) in params_dict.iter() {
                let key: String = key.extract()?;
                let value: String = value.to_string();
                query_params.push((key, value));
            }
            request_builder = request_builder.query(&query_params);
        }

        // Add headers
        if let Some(headers_dict) = headers {
            for (key, value) in headers_dict.iter() {
                let key: String = key.extract()?;
                let value: String = value.to_string();
                request_builder = request_builder.header(&key, &value);
            }
        }

        // Add body data
        if let Some(json_data) = json {
            // Try to use orjson for fast JSON encoding, fallback to standard json
            let json_str: String = py
                .import("orjson")
                .and_then(|orjson| {
                    let bytes = orjson.call_method1("dumps", (json_data,))?;
                    let bytes_obj: &PyAny = bytes;
                    let vec: Vec<u8> = bytes_obj.extract()?;
                    Ok(String::from_utf8(vec).unwrap_or_default())
                })
                .or_else(|_| {
                    // Fallback to standard json
                    py.import("json")?
                        .call_method1("dumps", (json_data,))?
                        .extract()
                })?;
            
            request_builder = request_builder
                .header("Content-Type", "application/json")
                .body(json_str);
        } else if let Some(body_data) = data {
            // Handle different data types
            if let Ok(s) = body_data.extract::<String>() {
                request_builder = request_builder.body(s);
            } else if let Ok(b) = body_data.extract::<Vec<u8>>() {
                request_builder = request_builder.body(b);
            } else if let Ok(dict) = body_data.downcast::<PyDict>() {
                // Form data
                let mut form_data = Vec::new();
                for (key, value) in dict.iter() {
                    let key: String = key.extract()?;
                    let value: String = value.to_string();
                    form_data.push((key, value));
                }
                request_builder = request_builder.form(&form_data);
            }
        }

        // Set timeout
        if let Some(timeout_secs) = timeout {
            request_builder = request_builder.timeout(Duration::from_secs_f64(timeout_secs));
        }

        // Execute request with proper redirect handling
        // If redirects are disabled, we need to create a new client
        let mut response = if let Some(redirects) = allow_redirects {
            if !redirects {
                let no_redirect_client = create_client_with_redirects(false)?;
                let mut new_request = no_redirect_client.request(method.clone(), &url);
                
                // Re-apply all parameters to the new request
                if let Some(params_dict) = params {
                    let mut query_params = Vec::new();
                    for (key, value) in params_dict.iter() {
                        let key: String = key.extract()?;
                        let value: String = value.to_string();
                        query_params.push((key, value));
                    }
                    new_request = new_request.query(&query_params);
                }
                
                if let Some(headers_dict) = headers {
                    for (key, value) in headers_dict.iter() {
                        let key: String = key.extract()?;
                        let value: String = value.to_string();
                        new_request = new_request.header(&key, &value);
                    }
                }
                
                if let Some(json_data) = json {
                    let json_str: String = py
                        .import("orjson")
                        .and_then(|orjson| {
                            let bytes = orjson.call_method1("dumps", (json_data,))?;
                            let bytes_obj: &PyAny = bytes;
                            let vec: Vec<u8> = bytes_obj.extract()?;
                            Ok(String::from_utf8(vec).unwrap_or_default())
                        })
                        .or_else(|_| {
                            py.import("json")?
                                .call_method1("dumps", (json_data,))?
                                .extract()
                        })?;
                    new_request = new_request
                        .header("Content-Type", "application/json")
                        .body(json_str);
                } else if let Some(body_data) = data {
                    if let Ok(s) = body_data.extract::<String>() {
                        new_request = new_request.body(s);
                    } else if let Ok(b) = body_data.extract::<Vec<u8>>() {
                        new_request = new_request.body(b);
                    } else if let Ok(dict) = body_data.downcast::<PyDict>() {
                        let mut form_data = Vec::new();
                        for (key, value) in dict.iter() {
                            let key: String = key.extract()?;
                            let value: String = value.to_string();
                            form_data.push((key, value));
                        }
                        new_request = new_request.form(&form_data);
                    }
                }
                
                if let Some(timeout_secs) = timeout {
                    new_request = new_request.timeout(Duration::from_secs_f64(timeout_secs));
                }
                
                new_request
            } else {
                request_builder
            }
        } else {
            request_builder
        };
        
        let mut response = response
            .send()
            .map_err(|e| {
                if e.is_timeout() {
                    Timeout::new_err(format!("Request timed out: {}", e))
                } else if e.is_connect() {
                    ConnectTimeout::new_err(format!("Connection timeout: {}", e))
                } else if e.is_redirect() {
                    TooManyRedirects::new_err(format!("Too many redirects: {}", e))
                } else {
                    ConnectionError::new_err(format!("Connection error: {}", e))
                }
            })?;

        // Extract response data
        let status_code = response.status().as_u16();
        let url = response.url().to_string();
        let mut headers = HashMap::new();
        
        for (name, value) in response.headers().iter() {
            let name_str = name.as_str().to_string();
            let value_str = value.to_str().unwrap_or("").to_string();
            headers.insert(name_str, value_str);
        }
        
        let body = response.bytes().ok();

        Ok(Response {
            status_code,
            url,
            headers,
            body,
        })
    }
}

/// HTTP Response wrapper
#[pyclass]
struct Response {
    status_code: u16,
    url: String,
    headers: HashMap<String, String>,
    body: Option<Bytes>,
}

#[pymethods]
impl Response {
    #[getter]
    fn status_code(&self) -> u16 {
        self.status_code
    }

    #[getter]
    fn url(&self) -> String {
        self.url.clone()
    }

    #[getter]
    fn headers(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        for (name, value) in self.headers.iter() {
            dict.set_item(name, value)?;
        }
        Ok(dict.into())
    }

    fn text(&mut self) -> PyResult<String> {
        if let Some(ref body) = self.body {
            String::from_utf8(body.to_vec())
                .map_err(|e| PyRuntimeError::new_err(format!("Failed to decode UTF-8: {}", e)))
        } else {
            Err(PyRuntimeError::new_err("Response body already consumed"))
        }
    }

    fn content(&mut self, py: Python) -> PyResult<PyObject> {
        if let Some(ref body) = self.body {
            Ok(PyBytes::new(py, body).into())
        } else {
            Err(PyRuntimeError::new_err("Response body already consumed"))
        }
    }

    fn json(&mut self, py: Python) -> PyResult<PyObject> {
        if let Some(ref body) = self.body {
            // Use orjson for fast JSON decoding, fallback to standard json
            let result = py
                .import("orjson")
                .and_then(|orjson| {
                    orjson.call_method1("loads", (PyBytes::new(py, body),))
                })
                .or_else(|_| {
                    let text = String::from_utf8(body.to_vec())
                        .map_err(|e| PyRuntimeError::new_err(format!("Failed to decode UTF-8: {}", e)))?;
                    let json_module = py.import("json")?;
                    json_module.call_method1("loads", (text,))
                })?;
            Ok(result.to_object(py))
        } else {
            Err(PyRuntimeError::new_err("Response body already consumed"))
        }
    }

    fn raise_for_status(&self) -> PyResult<()> {
        if self.status_code >= 400 {
            return Err(HTTPError::new_err(format!(
                "HTTP {} Error",
                self.status_code
            )));
        }
        Ok(())
    }
}

/// Fast request function using connection pooling
#[pyfunction]
fn request(
    py: Python,
    method: String,
    url: String,
    params: Option<&PyDict>,
    headers: Option<&PyDict>,
    data: Option<&PyAny>,
    json: Option<&PyAny>,
    timeout: Option<f64>,
    allow_redirects: Option<bool>,
    verify: Option<bool>,
) -> PyResult<Response> {
    // Use a global client pool for automatic connection reuse
    use once_cell::sync::Lazy;
    static CLIENT: Lazy<BlockingClient> = Lazy::new(|| {
        BlockingClient::builder()
            .pool_max_idle_per_host(100)
            .pool_idle_timeout(Some(Duration::from_secs(90)))
            .timeout(Duration::from_secs(30))
            .build()
            .expect("Failed to create HTTP client")
    });

    let method_enum = reqwest::Method::from_bytes(method.to_uppercase().as_bytes())
        .map_err(|e| PyValueError::new_err(format!("Invalid HTTP method: {}", e)))?;

    let mut request_builder = CLIENT.request(method_enum.clone(), &url);

    // Add query parameters
    if let Some(params_dict) = params {
        let mut query_params = Vec::new();
        for (key, value) in params_dict.iter() {
            let key: String = key.extract()?;
            let value: String = value.to_string();
            query_params.push((key, value));
        }
        request_builder = request_builder.query(&query_params);
    }

    // Add headers
    if let Some(headers_dict) = headers {
        for (key, value) in headers_dict.iter() {
            let key: String = key.extract()?;
            let value: String = value.to_string();
            request_builder = request_builder.header(&key, &value);
        }
    }

    // Add body data
    if let Some(json_data) = json {
        let json_str: String = py.import("json")?.call_method1("dumps", (json_data,))?.extract()?;
        request_builder = request_builder
            .header("Content-Type", "application/json")
            .body(json_str);
    } else if let Some(body_data) = data {
        if let Ok(s) = body_data.extract::<String>() {
            request_builder = request_builder.body(s);
        } else if let Ok(b) = body_data.extract::<Vec<u8>>() {
            request_builder = request_builder.body(b);
        } else if let Ok(dict) = body_data.downcast::<PyDict>() {
            let mut form_data = Vec::new();
            for (key, value) in dict.iter() {
                let key: String = key.extract()?;
                let value: String = value.to_string();
                form_data.push((key, value));
            }
            request_builder = request_builder.form(&form_data);
        }
    }

    // Set timeout
    if let Some(timeout_secs) = timeout {
        request_builder = request_builder.timeout(Duration::from_secs_f64(timeout_secs));
    }

    // Execute request with proper redirect handling
    let mut response = if let Some(redirects) = allow_redirects {
        if !redirects {
            let no_redirect_client = create_client_with_redirects(false)?;
            let mut new_request = no_redirect_client.request(method_enum.clone(), &url);
            
            // Re-apply all parameters
            if let Some(params_dict) = params {
                let mut query_params = Vec::new();
                for (key, value) in params_dict.iter() {
                    let key: String = key.extract()?;
                    let value: String = value.to_string();
                    query_params.push((key, value));
                }
                new_request = new_request.query(&query_params);
            }
            
            if let Some(headers_dict) = headers {
                for (key, value) in headers_dict.iter() {
                    let key: String = key.extract()?;
                    let value: String = value.to_string();
                    new_request = new_request.header(&key, &value);
                }
            }
            
            if let Some(json_data) = json {
                let json_str: String = py
                    .import("orjson")
                    .and_then(|orjson| {
                        let bytes = orjson.call_method1("dumps", (json_data,))?;
                        let bytes_obj: &PyAny = bytes;
                        let vec: Vec<u8> = bytes_obj.extract()?;
                        Ok(String::from_utf8(vec).unwrap_or_default())
                    })
                    .or_else(|_| {
                        py.import("json")?
                            .call_method1("dumps", (json_data,))?
                            .extract()
                    })?;
                new_request = new_request
                    .header("Content-Type", "application/json")
                    .body(json_str);
            } else if let Some(body_data) = data {
                if let Ok(s) = body_data.extract::<String>() {
                    new_request = new_request.body(s);
                } else if let Ok(b) = body_data.extract::<Vec<u8>>() {
                    new_request = new_request.body(b);
                } else if let Ok(dict) = body_data.downcast::<PyDict>() {
                    let mut form_data = Vec::new();
                    for (key, value) in dict.iter() {
                        let key: String = key.extract()?;
                        let value: String = value.to_string();
                        form_data.push((key, value));
                    }
                    new_request = new_request.form(&form_data);
                }
            }
            
            if let Some(timeout_secs) = timeout {
                new_request = new_request.timeout(Duration::from_secs_f64(timeout_secs));
            }
            
            new_request
        } else {
            request_builder
        }
    } else {
        request_builder
    };
    
    let response = response.send().map_err(|e| {
        if e.is_timeout() {
            Timeout::new_err(format!("Request timed out: {}", e))
        } else if e.is_connect() {
            ConnectTimeout::new_err(format!("Connection timeout: {}", e))
        } else if e.is_redirect() {
            TooManyRedirects::new_err(format!("Too many redirects: {}", e))
        } else {
            ConnectionError::new_err(format!("Connection error: {}", e))
        }
    })?;

    // Extract response data
    let status_code = response.status().as_u16();
    let url = response.url().to_string();
    let mut headers = HashMap::new();
    
    for (name, value) in response.headers().iter() {
        let name_str = name.as_str().to_string();
        let value_str = value.to_str().unwrap_or("").to_string();
        headers.insert(name_str, value_str);
    }
    
    let body = response.bytes().ok();

    Ok(Response {
        status_code,
        url,
        headers,
        body,
    })
}

/// Python module definition
#[pymodule]
fn _rapidhttp(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Client>()?;
    m.add_class::<Response>()?;
    m.add_function(wrap_pyfunction!(request, m)?)?;
    
    // Add exception types
    m.add("HTTPError", _py.get_type::<HTTPError>())?;
    m.add("ConnectionError", _py.get_type::<ConnectionError>())?;
    m.add("Timeout", _py.get_type::<Timeout>())?;
    m.add("ConnectTimeout", _py.get_type::<ConnectTimeout>())?;
    m.add("ReadTimeout", _py.get_type::<ReadTimeout>())?;
    m.add("TooManyRedirects", _py.get_type::<TooManyRedirects>())?;
    m.add("RequestException", _py.get_type::<RequestException>())?;
    m.add("URLRequired", _py.get_type::<URLRequired>())?;
    m.add("JSONDecodeError", _py.get_type::<JSONDecodeError>())?;

    Ok(())
}
