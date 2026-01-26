# Node Class Reference

The `Node` class represents a specific location in JSON data and allows navigation relative to that location. It provides a way to traverse and explore component data with lazy evaluation, meaning data is only accessed when explicitly requested through methods like `get_value()`, `exists()`, or iteration.

## Class Methods

### from_component_json

```python
@classmethod
from_component_json(cls, data)
```

Creates a `Node` instance from a JSON object. Note that a `Node` instance created from the component JSON only will not contain the deltas. While this can be useful for testing most policies, it will not represent a realistic component's data when testing `Check.get_all`.

- **data** (dict): A dictionary containing component metadata
- **Returns**: A new `Node` instance

Example:
```python
component_json = {
    "readme": {
        "lines": 50,
        "missing": False
    }
}
component_data = Node.from_component_json(component_json)
```

### from_component_json_file

```python
@classmethod
from_component_json_file(cls, file_path)
```

Creates a `Node` instance from a JSON file. Note that a `Node` instance created from the component JSON only will not contain the deltas. While this can be useful for testing most policies, it will not represent a realistic component's data when testing `Check.get_all`.

- **file_path** (str): Path to a JSON file containing component metadata
- **Returns**: A new `Node` instance

Example:
```python
component_data = Node.from_component_json_file("path/to/component.json")
```

### from_bundle_json

```python
@classmethod
from_bundle_json(cls, data)
```

Creates a `Node` instance from a bundle JSON object.

- **data** (dict): A dictionary containing bundle data
- **Returns**: A new `Node` instance

### from_bundle_file

```python
@classmethod
from_bundle_file(cls, file_path)
```

Creates a `Node` instance from a bundle JSON file.

- **file_path** (str): Path to a JSON file containing bundle data
- **Returns**: A new `Node` instance

## Data Access Methods

### get_value

```python
get_value(path=".")
```

Gets the raw value at the given path relative to this node.

- **path** (str): JSON path relative to this node (default: "." for this node's value)
- **Returns**: The raw value (dict, list, string, number, boolean, etc.)
- **Raises**: `ValueError` if the path is invalid or doesn't exist, `NoDataError` if data is not available yet

Example:
```python
# Get the current node's value
node = check.get_node(".config.database")
host = node.get_value(".host")  # Relative to .config.database
port = node.get_value(".port")  # Relative to .config.database

# Get the node's own value
database_config = node.get_value()  # Returns the entire database config object as a dict
```

### get_value_or_default

```python
get_value_or_default(path=".", default=None)
```

Gets the raw value at the given path relative to this node. If the value is missing for any reason, it returns the specified default instead.

- **path** (str): JSON path relative to this node (default: "." for this node's value)
- **default**: The value to return if there is no value at this path

Example:
```python
# Given this component JSON:
# {
#     "existing": {
#         "value": "hello"
#     }
# }

val = node.get_value_or_default(".existing.value", "goodbye") # val will be "hello"
val = node.get_value_or_default(".missing", "goodbye") # val will be "goodbye"
```


### get_node

```python
get_node(path)
```

Gets a Node at the given path relative to this node. Uses lazy evaluation - data is not accessed until value is needed.

- **path** (str): JSON path relative to this node
- **Returns**: A new Node instance at the specified path
- **Raises**: `ValueError` if the path syntax is invalid

### exists

```python
exists(path=".")
```

Checks if a path exists relative to this node.

Missing path behavior:

* Raises `NoDataError` **before** collectors finished (results in `pending` status).
* Returns `False` **after** collectors finished.

Example:
```python
host_node = check.get_node(".config.host")
if host_node.exists():
    host = host_node.get_value()
```

## Iteration Methods

### Iterating over Node

```python
for item in node:
    # Process item
```

Makes Node iterable. For dictionaries, yields keys. For arrays, yields Node objects.

- **For dict-like data**: Yields string keys
- **For array-like data**: Yields Node objects for each array element
- **Raises**: `ValueError` if the node doesn't point to a dict or array, `NoDataError` if data is not available yet

Example:
```python
# Iterate over dictionary keys
config_node = check.get_node(".config")
for key in config_node:
    print(f"Config key: {key}")

# Iterate over array elements
items_node = check.get_node(".items")
for item_node in items_node:
    name = item_node.get_value(".name")
    print(f"Item name: {name}")
```

### items

```python
items()
```

Get key-value pairs when this Node points to a dict-like structure.

- **Returns**: Iterator of (key, Node) tuples for dict-like data
- **Raises**: `ValueError` if the node doesn't point to a dictionary, `NoDataError` if data is not available yet

Example:
```python
config_node = check.get_node(".config")
for key, value_node in config_node.items():
    value = value_node.get_value()
    print(f"{key}: {value}")
```
