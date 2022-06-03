# API

!!! info

    We only have one api endpoint for `/members` and public to use. The more offcial REST API is under planning.

Base URL: `https://volunteer.coscup.org/api`

## GET /members

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
