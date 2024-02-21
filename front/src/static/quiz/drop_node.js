selecteed_node_id = 0;
selected_edge_id = 0;

$('.drag').draggable({
    appendTo: 'body',
    helper: 'clone'
});


$('#network_scheme').droppable({
    activeClass: 'active',
    hoverClass: 'hover',
    accept: ":not(.ui-sortable-helper)", // Reject clones generated by sortable
    drop: function (e, ui) {

        type = ui.draggable.prop('id')

        // Don't drop if network is animated
        if (PacketPlayer.getInstance().getPlayerPlay()){
            return;
        }

        // We add new device. Drop the network state.
        SetNetworkPlayerState(-1);

        // Save the network state if we gonna CTRL+Z.
        SaveNetworkObject();

        if (type === 'host'){

            let node_id = HostUid();
            nodes.push(
            {
                data: {id: node_id, label: node_id},
                position: {x: CalculateDropOffset(ui.position.left, ui.position.top).x, y: CalculateDropOffset(ui.position.left, ui.position.top).y},
                classes: ['host'],
                config: {
                    type: 'host',
                    label: node_id,
                },
                interface: [],
            });
        }
        else if (type === 'l2_switch'){
            let node_id = l2SwitchUid();
            nodes.push(
            {
                data: {id: node_id, label: node_id},
                position: {x: CalculateDropOffset(ui.position.left, ui.position.top).x, y: CalculateDropOffset(ui.position.left, ui.position.top).y},
                classes: ['l2_switch'],
                config: {
                    type: 'l2_switch',
                    label: node_id,
                    stp: 0,
                },
                interface: [],
            });
        }
        else if (type === 'l1_hub'){
            let node_id = l1HubUid();
            nodes.push(
            {
                data: {id: node_id, label: node_id},
                position: {x: CalculateDropOffset(ui.position.left, ui.position.top).x, y: CalculateDropOffset(ui.position.left, ui.position.top).y},
                classes: ['l1_hub'],
                config: {
                    type: 'l1_hub',
                    label: node_id,
                },
                interface: [],
            });
        }
        else if (type === 'l3_router'){
            let node_id = RouterUid();
            nodes.push(
            {
                data: {id: node_id, label: node_id},
                position: {x: CalculateDropOffset(ui.position.left, ui.position.top).x, y: CalculateDropOffset(ui.position.left, ui.position.top).y},
                classes: ['l3_router'],
                config: {
                    type: 'router',
                    label: node_id,
                },
                interface: [],
            });
        }
        else if (type === 'server'){
            let node_id = ServerUid();
            nodes.push(
            {
                data: {id: node_id, label: node_id},
                position: {x: CalculateDropOffset(ui.position.left, ui.position.top).x, y: CalculateDropOffset(ui.position.left, ui.position.top).y},
                classes: ['server'],
                config: {
                    type: 'server',
                    label: node_id,
                },
                interface: [],
            });
        }
        else {
            return;
        }

        DrawGraph();
        updateCounter(type, -1)
    }
});