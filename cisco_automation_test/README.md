# Exercises

## Exercise #1 
With Netmiko.

I want to configure L2 Cisco IOS switch and L3 Cisco IOS XE router:
- Create a VLAN on the switch
- Add the VLAN to the trunk interface towards the router
- Create a subinterface on the router for the VLAN
- Assign IP address on the subinterface
- Create an SVI on the L2 switch in the VLAN (to represent endpoint)

## Exercise #2
With PyATS.

I want to configure L2 port-channel between Nexus switch and L3 router:
- Configure LACP port-channel on Nexus switch (with 2 interfaces)
- Create a VLAN on the switch
- Add the VLAN to the port-channel
- Configure LACP port-channel on the L3 router
- Create a subinterface on the router for the VLAN
- Assign IP address on the subinterface
- Create an SVI on the Nexus switch in the VLAN (to represent endpoint)

## Exercise #3
With TextFSM. 

I want to parse output from the L2 switch and L3 router and Nexus switch:
- Show VLANs on L2 switch and Nexus switch
- Show physical interfaces on L2 switch and Nexus switch
- Show SVIs on L2 switch and Nexus switch
- Show physical interfaces on router
- Show L3 interfaces on router
- Show routes on router

## Exercise #4
With PyATS.

I want to parse output from the L2 switch and L3 router.
- Ping Nexus switch from the L2 switch and parse output
- Ping L2 switch from the Nexus switch and parse output

