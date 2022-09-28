# API Design Guide

## URIs

#### URIs should represent resources, not actions

#### A trailing slash should not be included in URIs

The trailing slash adds no semantic value to the URL. 
The two URIs (with and without trailing slash) are treated as different identifiers.

#### Prefer hyphens (-) to underscores (_) in URIs

Hyphens improve readability of names in long path segments. 
URLs are often highlighted by underline in text editors and browsers.
The underscore separator can be obscured or completely hidden by this underlining.

## HTTP Methods

#### GET

**Idempotent:** Yes

Use `GET` method to retrieve a representation of a resource.

#### POST

**Idempotent:** No

Use `POST` method to create a new resource in a collection.

#### PATCH

**Idempotent:** No

Use `PATCH` method to partially update a resource.

Usually patch may contain any number (one or more) of fields of a resource to be updated.

#### PUT

**Idempotent:** Yes

Use `PUT` method to create or update an existing resources.

#### DELETE

**Idempotent:** Yes

Use `DELETE` method to delete a resource. 
If a resource doesn't exist, server must return `404 Not Found` status code.

## HTTP Status codes

#### 200 OK

The `200 OK` status code indicates that the request has succeeded.

#### 201 Created

The `201 Created` indicates that the request has been fulfilled and has resulted in
one or more new resources being created. 

#### 204 No Content

The `204 No Content` status code indicates that the server has successfully 
fulfilled the request and that there is no additional content to send in the
response content.

Use the `204 No Content` when:
* The endpoint doesn't return any meaningful content. 
* Deleting a resource results in empty response to be sent to client.

#### 404 Not found

The `404 Not Found` indicates that the server did not find a current representation
for the target resource.

Use the `404 Not Found` when:
* The URI is not valid.
* The URI is valid, but requested resource doesn't exist.

#### 422 Unprocessable Content

The `422 Unprocessable Content` indicates that the server understands the content
of a request and the syntax of the request is correct, but it was unable to process
the contained instructions.

Use the `422 Unprocessable Content` when:
* The request data has failed validation.

#### 

## Pagination

_TBA_

## Metadata 

_TBA_

## OpenAPI Schema

#### Add `operation_id` to endpoints

The `operation_id` field is used by API client generators and generates method 
  names based on its value.

#### Add `tags` to endpoints

Tags are used to group individual endpoints in API documentation page.

#### Document endpoint response schema

#### Document expected HTTP error codes

## References

1. [REST API Design Rulebook, by Mark Masse](https://www.oreilly.com/library/view/rest-api-design/9781449317904/index.html)
2. [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md)
3. [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)