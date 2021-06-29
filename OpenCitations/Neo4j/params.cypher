/*
Unwind a list

Simple: [1, 2, 3]

Complex:
[
 {"id": 42, "foo": "Bar"},
 {"id": 43, "foo": "Bar"}
]
*/
UNWIND $input_data AS row
RETURN row;

MATCH (n:Pub)
WHERE n.doi in $input_data
RETURN *;