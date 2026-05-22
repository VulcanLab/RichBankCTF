// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/BankVault.sol";

contract Deploy is Script {
    address constant OWNER     = 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266;
    uint256 constant OWNER_KEY = 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80;

    // 客戶帳號（Anvil #4~#19，用來模擬存款）
    uint256[16] internal customerKeys = [
        uint256(0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926b),
        uint256(0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba),
        uint256(0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e),
        uint256(0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356),
        uint256(0xdbda1821b80551c9d65939329250132c0f4b6fc7b01104e82c6f9d6f4d9a0c67),
        uint256(0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6),
        uint256(0xf214f2b2cd398c806f84e317254e0f0b801d0643303237d97a22a48e01628897),
        uint256(0x701b615bbdfb9de65240bc28bd21bbc0d996645a3dd57e7b12bc2bdf6f192c82),
        uint256(0xa267530f49f8280200edf313ee7af6b827f2a8bce2897751d06a843f644967b2),
        uint256(0x47c99abed3324a2707c28affff1267e45918ec8c3f20b8aa892e8b065d2942dd),
        uint256(0xc526ee95bf44d8fc405a158bb884d9d1238d99f0612e9f33d006bb0789009aaa),
        uint256(0x8166f546bab6da521a8369cab06c5d2b9e46670292d85c875ee9ec20e84ffb61),
        uint256(0xea6c44ac03bff858b476bba28179e5e3200af9ac3b8e7b55b4de3a8c8f9c6a9d),
        uint256(0x689af8efa8c651a91ad287602527f3af2fe9f6501a7ac4b061667b5a93e037fd),
        uint256(0xde9be858da4a475276426320d5e9262ecfc3ba460bfac56360bfa6c4c28b4ee0),
        uint256(0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e)
    ];

    function run() external {
        // 從環境變數讀取動態產生的 manager/clerk 地址
        address managerAddr = vm.envAddress("MANAGER_ADDRESS");
        address agentAddr   = OWNER; // backend 用 Owner key 代表 agent

        vm.startBroadcast(OWNER_KEY);
        BankVault vault = new BankVault{value: 1000 ether}(managerAddr, agentAddr);
        vm.stopBroadcast();

        // 充值並讓客戶存款
        uint256[16] memory amounts = [
            uint256(50 ether), 120 ether, 30 ether,  200 ether,
            75 ether,  310 ether, 88 ether,  150 ether,
            45 ether,  260 ether, 95 ether,  180 ether,
            60 ether,  400 ether, 110 ether, 220 ether
        ];

        vm.startBroadcast(OWNER_KEY);
        for (uint256 i = 0; i < 16; i++) {
            address customerAddr = vm.addr(customerKeys[i]);
            payable(customerAddr).transfer(amounts[i] + 0.1 ether);
        }
        vm.stopBroadcast();

        for (uint256 i = 0; i < 16; i++) {
            vm.startBroadcast(customerKeys[i]);
            vault.deposit{value: amounts[i]}();
            vm.stopBroadcast();
        }

        console.log("VAULT_ADDRESS=%s", address(vault));
    }
}
