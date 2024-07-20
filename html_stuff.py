# By having it as strings in Python I make it more obvious it is loaded
# only once. Also, less of a hassle.

search_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
    <ShortName>Go</ShortName>  
    <Description>Custom Redirect Service</Description> 
    <Url type="text/html" template="http://g/{{searchTerms}}/" method="GET"/> 
    <Image height="16" width="16" type="image/x-icon">data:image/x-icon;base64,YOUR_BASE64_FAVICON_DATA</Image>
</OpenSearchDescription>
"""

css = """
body {
  font-family: monospace, "monoidregular", "Roboto";
  max-width: 600px;
}

/* General Form Styling */
form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.form-container {
  display: flex;
  flex-direction: column; /* Optional: to arrange rows vertically */
}

.row {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}

.col-1, .col-2, .col-3 {
  margin-left: 1em;
  margin-right: 1em;
}

#saving, #deleting {
    margin: auto;
}

/* Text Input Styling */
input[type="text"], input[type="checkbox"] {
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: border-color 0.3s ease;
}

input[type="text"]:focus,
input[type="checkbox"]:focus {
  outline: none;
  border-color: #007bff; 
}

/* Read-Only Text Input Styling */
input[type="text"]:read-only {
  background-color: #f5f5f5; 
  border-color: #e9ecef;    
  color: #6c757d;          
  cursor: default;          
}

input[type="checkbox"] {
  width: 2.2rem;
  height: 2.2rem;
  appearance: none;
}

input[type="checkbox"]:checked {
  background-color: #007bff;
  border-color: #007bff;  
}

input[type="checkbox"]:checked::before {
  content: "\2713";             /* Unicode character for checkmark */
  display: block;
  text-align: center;
  color: white;
  font-size: 1rem; 
}

/* Button Styling */
button[type="submit"] {
  background-color: #007bff; 
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease;
}

button[type="submit"]:hover {
  background-color: #0056b3;
}

h2 {
  font-size: 2.5rem; /* Adjust the size to your preference */
  font-weight: 600; /* Semi-bold font weight */
  margin-bottom: 1.5rem; /* Add some space below the heading */
}

h2 {
  text-align: center;     /* Center the heading */
  text-transform: uppercase; /* Make it uppercase */
  letter-spacing: 2px;      /* Add letter spacing */
  color: #333;           /* Darker text color */
}
"""

settings_page_outer = """
<!DOCTYPE html>
<html>
<head>
<title>Settings</title>
<style>
{css}
</style>
</head>
<body>
    <h2>Settings</h2>
    <form method="post" action="/settings"> 
        <div id="saving" class="form-container">
            {saving_rows}
        </div>
        <button type="submit">Save Changes</button>
    </form>

    <form method="post" action="/settings"> 
        <input type="hidden" name="action" value="delete">
        <div id="deleting" class="form-container">
            {deleting_rows}
        </div>
        <button type="submit">Delete Selected</button>
    </form>
</body>
</html>
"""

def get_rows(redirects, kind="saving"):
    table_rows = ""
    for i, (path, url) in enumerate(redirects.items()):
        path = path.replace("/", "")
        if kind=="saving":
            extra_row = ""
            readonly = ""
        else:
            extra_row = f"""<div class="col-3"><input type="checkbox" name="delete-{path}" value="{path}"></div>"""
            readonly = "readonly"
        table_rows += f"""
            <div class="row">
                <div class="col-1"><input type="text" name="path-{path}" value="{path}" {readonly}></div>
                <div class="col-2"><input type="text" name="url{i}" value="{url}" {readonly}></div>
                {extra_row}
            </div>
        """
    else:
        if kind=="saving":
            i = len(redirects)
            table_rows += f"""
            <div class="row">
                <div class="col-1"><input type="text" name="path{i}" value=""></div>
                <div class="col-2"><input type="text" name="url{i}" value=""></div>
                <div class="col-3"></div>
            </div>
    """
    return table_rows

def generate_settings_page(redirects):
    saving_rows = get_rows(redirects, kind="saving")
    deleting_rows = get_rows(redirects, kind="deleting")

    return settings_page_outer.format(saving_rows=saving_rows, deleting_rows=deleting_rows, css=css)
