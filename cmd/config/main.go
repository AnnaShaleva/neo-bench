package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/k14s/ytt/pkg/cmd/template"
	"github.com/nspcc-dev/neo-go/pkg/config"
	"gopkg.in/yaml.v2"
)

const (
	configPath       = "../.docker/ir/"
	rpcConfigPath    = "../.docker/rpc/"
	templateDataFile = "template.data.yml"
	singleNodeName   = "single"
)

var (
	nFlag             = flag.Int("n", 5, "number of nodes in the experiment")
	createComposeFile = flag.Bool("compose", false, "create default docker-compose file for templates")
	createDataFile    = flag.Bool("data", false, "create default data file for templates")
	goTemplateFile    = flag.String("go-template", "", "configuration template file for Go node")
	goDB              = flag.String("go-db", "leveldb", "database for Go node")
	sharpTemplateFile = flag.String("sharp-template", "", "configuration template file for C# node")
	sharpDB           = flag.String("sharp-db", "LevelDBStore", "database for C# node")
)

func main() {
	flag.Parse()

	nNodes := *nFlag
	if nNodes == 0 {
		log.Fatalf("invalid number of nodes specified (use -n flag)")
	}

	if ok := *createDataFile; ok {
		err := generateData(nNodes)
		if err != nil {
			log.Fatalf("failed to generate data: %v", err)
		}
		return
	}

	if ok := *createComposeFile; ok {
		err := generateCompose(nNodes)
		if err != nil {
			log.Fatalf("failed to generate docker-compose file: %v", err)
		}
		return
	}

	tempDir, err := ioutil.TempDir("./", "")
	if err != nil {
		log.Fatalf("failed to create temporary directory: %v", err)
	}
	defer func() {
		err := os.RemoveAll(tempDir)
		if err != nil {
			log.Fatalf("failed to remove temporary directory: %v", err)
		}
	}()

	if templateFile := *goTemplateFile; templateFile != "" {
		err := convertTemplateToPlain(templateFile, tempDir)
		if err != nil {
			log.Fatalf("failed to call ytt for Go template: %v", err)
		}
		err = generateGoConfig(tempDir+"/"+templateFile, *goDB)
		if err != nil {
			log.Fatalf("failed to generate Go configurations: %v", err)
		}
	}
	if templateFile := *sharpTemplateFile; templateFile != "" {
		err := convertTemplateToPlain(templateFile, tempDir)
		if err != nil {
			log.Fatalf("failed to call ytt for C# template: %v", err)
		}
		err = generateSharpConfig(tempDir+"/"+templateFile, *sharpDB)
		if err != nil {
			log.Fatalf("failed to generate C# configurations: %v", err)
		}
	}
}

func convertTemplateToPlain(templatePath string, tempDir string) error {
	filePath := configPath + templatePath
	dataPath := configPath + templateDataFile
	cmd := template.NewCmd(template.NewOptions())
	cmd.SetArgs([]string{"-f", filePath, "-f", dataPath, "--output-files", tempDir})
	err := cmd.Execute()
	if err != nil {
		return err
	}
	return nil
}

func generateGoConfig(templatePath string, database string) error {
	f, err := os.Open(templatePath)
	if err != nil {
		return fmt.Errorf("failed to open template: %v", err)
	}
	defer f.Close()
	decoder := yaml.NewDecoder(bufio.NewReader(f))
	for i := 0; ; i++ {
		var template config.Config
		err := decoder.Decode(&template)
		if err == io.EOF {
			break
		}
		if err != nil {
			return fmt.Errorf("unable to decode node template #%d: %v", i, err)
		}
		template.ApplicationConfiguration.DBConfiguration.Type = database
		var configFile string
		nodeName, err := nodeNameFromSeedList(template.ApplicationConfiguration.NodePort, template.ProtocolConfiguration.SeedList)
		if err != nil {
			// it's an RPC node then
			configFile = rpcConfigPath + "go.protocol.yml"
			template.ApplicationConfiguration.UnlockWallet.Path = ""
		} else {
			configFile = configPath + "go.protocol.privnet." + nodeName + ".yml"
		}
		bytes, err := yaml.Marshal(template)
		if err != nil {
			return fmt.Errorf("could not marshal config for node #%s: %v", nodeName, err)
		}
		err = ioutil.WriteFile(configFile, bytes, 0644)
		if err != nil {
			return fmt.Errorf("could not write config for node #%s: %v", nodeName, err)
		}
	}
	return nil
}

func generateSharpConfig(templatePath string, storageEngine string) error {
	f, err := os.Open(templatePath)
	if err != nil {
		return fmt.Errorf("failed to open template: %v", err)
	}
	defer f.Close()
	decoder := yaml.NewDecoder(bufio.NewReader(f))
	for i := 0; ; i++ {
		var template SharpTemplate
		err := decoder.Decode(&template)
		if err == io.EOF {
			break
		}
		if err != nil {
			return fmt.Errorf("unable to decode node template #%d: %v", i, err)
		}
		template.ApplicationConfiguration.Storage.Engine = storageEngine
		var configFile string
		nodeName, err := nodeNameFromSeedList(template.ApplicationConfiguration.P2P.Port, template.ProtocolConfiguration.SeedList)
		if err != nil {
			// it's an RPC node then
			configFile = rpcConfigPath + "sharp.config.json"
			template.ApplicationConfiguration.UnlockWallet = UnlockWallet{}

		} else {
			configFile = configPath + "sharp.config." + nodeName + ".json"
		}
		err = writeJSON(configFile, SharpConfig{
			ApplicationConfiguration: template.ApplicationConfiguration,
			ProtocolConfiguration:    template.ProtocolConfiguration,
		})
		if err != nil {
			return fmt.Errorf("could not write JSON config file for node #%s: %v", nodeName, err)
		}
	}
	return nil
}

func writeJSON(path string, obj interface{}) error {
	bytes, err := json.Marshal(obj)
	if err != nil {
		return err
	}
	err = ioutil.WriteFile(path, bytes, 0644)
	if err != nil {
		return err
	}
	return nil
}

func nodeNameFromSeedList(port uint16, seedList []string) (string, error) {
	suffix := ":" + strconv.Itoa(int(port))
	for _, seed := range seedList {
		if strings.HasSuffix(seed, suffix) {
			node := strings.TrimSuffix(seed, suffix)
			if node == "node" {
				return singleNodeName, nil
			} else {
				return strings.TrimPrefix(node, "node_"), nil
			}
		}
	}
	return "", fmt.Errorf("node with port %v is not in the seed list", port)
}

func generateData(n int) error {
	defaultData := &Data{
		NodesInfo: []NodeInfo{
			{
				NodeName:           "single",
				NodePort:           20332,
				NodeRpcPort:        20331,
				NodeMonitoringPort: 20004,
				NodePprofPort:      20011,
				NodePrometheusPort: 40001,
				ValidatorHash:      "02b3622bf4017bdfe317c58aed5f4c753f206b7db896046fa7d774bbc4bf7f8dc2",
				WalletPassword:     "one",
			},
			{
				NodeName:           "rpc",
				NodePort:           20332,
				NodeRpcPort:        20331,
				NodeMonitoringPort: 2112,
				NodePprofPort:      30005,
				NodePrometheusPort: 40005,
				ValidatorHash:      "",
				WalletPassword:     "",
			},
			{
				NodeName:           "1",
				NodePort:           20333,
				NodeRpcPort:        30333,
				NodeMonitoringPort: 20001,
				NodePprofPort:      30001,
				NodePrometheusPort: 40001,
				ValidatorHash:      "02b3622bf4017bdfe317c58aed5f4c753f206b7db896046fa7d774bbc4bf7f8dc2",
				WalletPassword:     "one",
			},
			{
				NodeName:           "2",
				NodePort:           20334,
				NodeRpcPort:        30334,
				NodeMonitoringPort: 20002,
				NodePprofPort:      30002,
				NodePrometheusPort: 40002,
				ValidatorHash:      "02103a7f7dd016558597f7960d27c516a4394fd968b9e65155eb4b013e4040406e",
				WalletPassword:     "two",
			},
			{
				NodeName:           "3",
				NodePort:           20335,
				NodeRpcPort:        30335,
				NodeMonitoringPort: 20003,
				NodePprofPort:      30003,
				NodePrometheusPort: 40003,
				ValidatorHash:      "03d90c07df63e690ce77912e10ab51acc944b66860237b608c4f8f8309e71ee699",
				WalletPassword:     "three",
			},
			{
				NodeName:           "4",
				NodePort:           20336,
				NodeRpcPort:        30336,
				NodeMonitoringPort: 20004,
				NodePprofPort:      30004,
				NodePrometheusPort: 40004,
				ValidatorHash:      "02a7bc55fe8684e0119768d104ba30795bdcc86619e864add26156723ed185cd62",
				WalletPassword:     "four",
			},
		},
	}
	for i := 4; i < n; i++ {
		defaultData.NodesInfo = append(defaultData.NodesInfo, NodeInfo{
			NodeName:           strconv.Itoa(i + 1),
			NodePort:           uint16(20333 + i),
			NodeRpcPort:        uint16(30333 + i),
			NodeMonitoringPort: uint16(20001 + i),
			NodePprofPort:      uint16(30001 + i),
			NodePrometheusPort: uint16(40001 + i),
		})
	}
	bytes, err := yaml.Marshal(defaultData)
	if err != nil {
		return err
	}
	bytes = append([]byte("#@data/values\n---\n"), bytes...)
	err = ioutil.WriteFile(configPath+"template.data.yml", bytes, 0644)
	if err != nil {
		return err
	}
	return nil
}

func generateCompose(n int) error {
	defaultCompose := Compose{
		Version: "2.4",
		Networks: map[string]Network{
			"neo_go_network": {
				Name: "neo_go_network",
				Ipam: Ipam{
					Config: []Config{{
						Subnet:  "172.200.0.0/24",
						Gateway: "172.200.0.254",
					}},
				},
			}},
		Services: map[string]Service{},
	}
	port := 30333
	dependsOn := make(map[string]Condition)
	for i := 0; i < n; i++ {
		nodePort := port + i
		nStr := strconv.Itoa(i + 1)
		s := Service{
			Labels:        []string{"stats"},
			ContainerName: "neo_go_node_" + nStr,
			Image:         "registry.nspcc.ru/neo-bench/neo-go:bench",
			Logging: Logging{
				Driver: "none",
			},
			Command: "node --config-path /config --privnet",
			Healthcheck: Healthcheck{
				Interval: "5s",
				Retries:  15,
				Test:     []string{"CMD", "sh", "-c", "echo | nc 127.0.0.1 " + strconv.Itoa(nodePort)},
				Timeout:  "10s",
			},
			Environment: []string{"ACC=dump.acc"},
			Volumes: []string{
				fmt.Sprintf("./go.protocol.privnet.%d.yml:/config/protocol.privnet.yml", i+1),
				"./logs/:/logs/",
			},
		}
		if i == 0 || i == 4 || i == 9 || i == 19 || i == 29 || i == 49 || i == 74 || i == 99 {
			s.Logging.Driver = ""
		}
		if i < 4 {
			s.Volumes = append(s.Volumes, fmt.Sprintf("./wallet.%d.json:/config/wallet.json", i+1))
		}
		defaultCompose.Services["node_"+nStr] = s
		dependsOn[fmt.Sprintf("node_%d", i+1)] = Condition{
			Condition: "service_healthy",
		}
	}
	defaultCompose.Services["healthy"] = Service{
		Image:     "alpine",
		DependsOn: dependsOn,
	}
	bytes, err := yaml.Marshal(defaultCompose)
	if err != nil {
		return err
	}
	err = ioutil.WriteFile(configPath+"docker-compose.network.yml", bytes, 0644)
	if err != nil {
		return err
	}
	return nil
}
