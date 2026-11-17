// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract AgriAuditAnchor {
    address public immutable owner;
    mapping(address => bool) public authorizedWriters;
    mapping(bytes32 => bool) public anchored;

    event WriterAuthorizationChanged(address indexed writer, bool authorized);
    event AuditHashAnchored(
        bytes32 indexed eventHash,
        address indexed submitter,
        uint256 timestamp
    );

    error Unauthorized();
    error EmptyHash();
    error AlreadyAnchored();

    constructor() {
        owner = msg.sender;
        authorizedWriters[msg.sender] = true;
        emit WriterAuthorizationChanged(msg.sender, true);
    }

    function setWriter(address writer, bool authorized) external {
        if (msg.sender != owner) revert Unauthorized();
        authorizedWriters[writer] = authorized;
        emit WriterAuthorizationChanged(writer, authorized);
    }

    function anchorAuditHash(bytes32 eventHash) external {
        if (!authorizedWriters[msg.sender]) revert Unauthorized();
        if (eventHash == bytes32(0)) revert EmptyHash();
        if (anchored[eventHash]) revert AlreadyAnchored();

        anchored[eventHash] = true;
        emit AuditHashAnchored(eventHash, msg.sender, block.timestamp);
    }
}
