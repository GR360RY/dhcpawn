## Object Types

For every obeject we'd like to have comments filed as a separate modifiable field. 

### Group 

Fields: ( all below are dhcpStatements )

1. next-server
2. filename
3. default-lease-time
4. max-lease-time

### Hosts

### Subnets

1. Name of the subnet should be identical to the CN.
2. The only required field in Subnet is NetMask.
3. For fields we would like to provide default options:

ex: lease time, default gateway ( last IP in subnet )

4. Provide human readable string for each optional field.
5. Add DHCP_DEPLOYED field (Boolean).

### Pool

1. must have a range.

### IPs

1. Can be related to subnets outside of the ranges. IP ranges should not overlay with those IPs. 
2. IPs can be set explicitly through the API




