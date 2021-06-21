<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
    <title>{{!name}}</title>
    <style type="text/css">
  body {
    font-family: arial;
  }

  table {
    border: 1px solid #ccc;
    width: 80%;
    margin:0;
    padding:0;
    border-collapse: collapse;
    border-spacing: 0;
    margin: 0 auto;
  }

  table thead {
    background-color: #337ab7;
    color: #fff;   
  }

  table tr {
    border: 1px solid #ddd;
    padding: 5px;
  }

  table th, table td {
    padding: 10px;
    text-align: left;
  }

  table th {
    text-transform: uppercase;
    font-size: 14px;
    letter-spacing: 1px;
  }

  table tbody tr:hover {
      background-color: #ced4da;
      color: #000;
    }

  @media screen and (max-width: 600px) {

    table {
      border: 0;
    }

    table thead {
      display: none;
    }

    table tr {
      margin-bottom: 10px;
      display: block;
      border-bottom: 2px solid #ddd;
    }

    table td {
      display: block;
      text-align: right;
      font-size: 13px;
      border-bottom: 1px dotted #ccc;
    }

    table td:last-child {
      border-bottom: 0;
    }

    table td:before {
      content: attr(data-label);
      float: left;
      text-transform: uppercase;
      font-weight: bold;
    }
  }

.note{max-width: 80%; margin: 0 auto;}
    </style>

</head>
<body>
%for table in tables:
<div class="note">
<h3>{{!table["name"]}}</h3>
</div>
<table>
  <thead>
    <tr>
	%for t in table["titles"]:
      <th>{{!t}}</th>
	%end
    </tr>
  </thead>
  <tbody>
	%for row in table["data"]:
    <tr>
		%for col in row:
			<td data-label="">{{col}}</td>
		%end
    </tr>
	%end
  </tbody>
</table>
%end

</body>
</html>
