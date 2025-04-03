# Changes
- return paginated response when sending users (include link to next and previous page and retrieve page from request url)
- make retrieving users + filtering + searching a single endpoint
- assigning baladiyas should first delete all existing assignments and then reassign
- send the users existing assignments (wilaya + baladiya)
- assigning baladiyas should except multiple baladiya ids and not expect any wilaya
- assigning baladiya should accept baladiya ids not names
- get user id from user body not url
- use method patch instead of post in role assignment as this is effectively updating not assigning

# Notes
- to ensure security validate both that the user is logged in and that he has admin privileges to assign roles + baladiyat
- check if user role is a valid role before assignment
