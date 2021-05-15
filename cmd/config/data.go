package main

type Data struct{
	NodesInfo []NodeInfo `yaml:"nodes_info"`
}
type NodeInfo struct{
	NodeName string `yaml:"node_name"`
	NodePort uint16 `yaml:"node_port"`
	NodeRpcPort uint16 `yaml:"node_rpc_port"`
	NodeMonitoringPort uint16 `yaml:"node_monitoring_port"`
	NodePprofPort uint16 `yaml:"node_pprof_port"`
	NodePrometheusPort uint16 `yaml:"node_prometheus_port"`
	ValidatorHash string `yaml:"validator_hash"`
	WalletPassword string `yaml:"wallet_password"`
}
