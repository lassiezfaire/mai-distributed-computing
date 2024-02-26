#!/bin/bash
sleep 10

mongosh --host 192.168.1.69:27017 <<EOF
  var config = {
    "_id": "mongocluster",
    "members": [{
            "_id": 0,
            "host": "192.168.1.69:27017"
        },
        {
            "_id": 1,
            "host": "192.168.1.69:27018"
        },
        {
            "_id": 2,
            "host": "192.168.1.69:27019"
        }
    ]
  }
  rs.initiate(config);
EOF