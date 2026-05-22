// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BankVault {
    address public owner;
    address public managerAddress;
    address public agentAddress;

    uint256 public vaultBalance;

    mapping(address => uint256) public customerDeposits;
    mapping(address => Role) public roles;

    enum Role { Guest, Clerk, Manager }

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event VaultTransfer(address indexed to, uint256 amount);
    event AgentTransfer(address indexed from, address indexed to, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    modifier onlyManager() {
        require(msg.sender == managerAddress, "Only manager");
        _;
    }

    modifier onlyAgent() {
        require(msg.sender == agentAddress, "Only agent");
        _;
    }

    constructor(address _manager, address _agent) payable {
        owner = msg.sender;
        managerAddress = _manager;
        agentAddress = _agent;
        vaultBalance = msg.value;
    }

    // Guest: 存款
    function deposit() public payable {
        customerDeposits[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    // Guest: 提自己的存款
    function withdrawMyDeposit(uint256 amount) public {
        require(customerDeposits[msg.sender] >= amount, "Insufficient balance");
        customerDeposits[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
        emit Withdrawn(msg.sender, amount);
    }

    // Manager: 轉走金庫資金（題三）
    function transferFromVault(address to, uint256 amount) public onlyManager {
        require(vaultBalance >= amount, "Insufficient vault balance");
        vaultBalance -= amount;
        payable(to).transfer(amount);
        emit VaultTransfer(to, amount);
    }

    // Agent: 代替客戶轉帳（題四 Confused Deputy）
    function agentTransfer(address from, address to, uint256 amount) public onlyAgent {
        require(customerDeposits[from] >= amount, "Insufficient customer balance");
        customerDeposits[from] -= amount;
        payable(to).transfer(amount);
        emit AgentTransfer(from, to, amount);
    }

    function getVaultBalance() public view returns (uint256) {
        return vaultBalance;
    }

    function getCustomerBalance(address customer) public view returns (uint256) {
        return customerDeposits[customer];
    }

    receive() external payable {
        vaultBalance += msg.value;
    }
}
