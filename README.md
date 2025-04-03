Colour Replacer for JSON Files
A simple tool to replace color values in JSON files based on specified rules or mappings. This utility is designed to help developers and designers efficiently update color codes (e.g., HEX, RGB) in JSON configuration files or datasets.

Features
Replace color values (e.g., #FF0000 to #00FF00) in JSON files.
Supports custom color mappings via a configuration file.
Preserves JSON structure and formatting.
Lightweight and easy to use.

Usage
Run the tool with the following command:

text

Collapse

Wrap

Copy
colour-replacer [input-file] [output-file] [mapping-file]
input-file: Path to the JSON file you want to modify.
output-file: Path where the modified JSON will be saved.
mapping-file: Path to the JSON file containing color replacement rules (optional).
Example
bash

Collapse

Wrap

Copy
colour-replacer input.json output.json colors.json
Sample Mapping File (colors.json)
json

Collapse

Wrap

Copy
{
  "#FF0000": "#00FF00",
  "#0000FF": "#FFFF00"
}
This replaces all instances of red (#FF0000) with green (#00FF00) and blue (#0000FF) with yellow (#FFFF00).

Requirements
Node.js vX.X.X or higher (if applicable).
Python vX.X.X or higher (if applicable).
Contributing
Feel free to submit issues or pull requests if you have suggestions or improvements!
