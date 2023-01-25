# API

## Planning REST API

The new REST API is now under planning and heavy development. Any update or announcement
in the future will be published here.

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_api_flow.svg">
    <img alt="coscup_volunteer_api_flow" src="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_api_flow.svg">
  </a>
  <figcaption>Authorization flow, <small><a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_api_flow.svg">[original]</a></small></figcaption>
</figure>

 - [API Docs](#api-docs)
 - [Gettting started](#getting-started)

### Planning

=== "Login"
    - [x] API Token.
    - [ ] Remove all sessions.

=== "User"
     - [x] User self info
        - [x] GET
        - [x] POST: bank, resume, address, dietary habit, real profile

=== "Users"
    - [ ] Get users public info

=== "Projects"
    - [x] List all projects.
    - [x] Creat a project.
    - [ ] Update traffic subsidy.

=== "Teams"
    - [x] List all Teams.
    - [x] Create a new team.
    - [x] Add / delete chiefs
    - [x] Add / delete members.
    - [ ] List available forms.

=== "Tasks"
    - [x] List all tasks.

## API Docs

The interactive API docs are provided by [Swagger UI](https://swagger.io/tools/swagger-ui/)
included in [fastAPI](https://fastapi.tiangolo.com/).

 - Docs: [https://volunteer.coscup.org/api/docs](/api/docs)
 - ... or [Redoc](/api/redoc) style.

## Getting started

### Creating an application

!!! Warning ""

    Right now we do not support the application identifier way to create
    the volunteer app, but we are working in progress.

### User authorization

1. Get the temporary and ont-time-use exchange username, password from [here](/setting/api_token).
2. Submit a POST request to [/api/token](/api/docs#/login/exchange_access_token_token_post) to get the api token.
3. Submit the request with a header `Authorization` with a value of `Bearer` plus the api token.
4. ... or make a try in the [api docs](/api/docs).

## Deprecated API

!!! Warning

    The api endpoint of `/members` is deprecated, using `/members/{pid}` instead.

### GET /members

To show all the members in the project.

| Name  | Type     | Description |
| ----- | -------- | ----------- |
| `pid` | `string` | Project ID  |

=== "cURL"

    ``` bash
    curl https://volunteer.coscup.org/api/members?pid=2022
    ```

=== "Response"

     - Status: `200`
     - Content Type: `application/json`

    ``` json
    {
      "data": [
        {
          "name": "總召組 - General Coordinator",
          "tid": "coordinator"
          "chiefs": [
            {
              "email_hash": "86d3bee674f1962af04b0192f0c959f3",
              "name": "球魚/Ballfish"
            },
            {
              "email_hash": "9c08215f31eb6005a25be6521bf47b0a",
              "name": "Denny Huang"
            },
            {
              "email_hash": "4b0cdd9418513546c11c12f181f51c0f",
              "name": "Toomore"
            }
          ],
          "members": [
            {
              "email_hash": "80bba454a8b37dba920e8787f78b3b81",
              "name": "Singing"
            },
            {
              "email_hash": "8ba17c693edf1f29ae77d64443ac242e",
              "name": "nfsnfs"
            }
          ],
        },
        ...
      ]
    }
    ```
