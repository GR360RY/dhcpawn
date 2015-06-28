Running the client locally
--------------------------

This section describes a setup intended for development.

We'll assume that:
- you have Node.js installed
- the DHCPawn API is listening on port 10080

**Prerequisites:**

    npm i -g grunt-cli

**Install local dependencies:**

    npm install

**Start the development server:**

    grunt runserver

Visit http://127.0.0.1:8090/ to see whether the above steps worked.

### Other useful commands

**Check JavaScript code with JSHint**

    grunt jshint
