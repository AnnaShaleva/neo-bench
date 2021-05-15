package main

type Compose struct {
	Version  string             `yaml:"version"`
	Networks map[string]Network `yaml:"networks"`
	Services map[string]Service `yaml:"services"`
}
type Network struct {
	Name string `yaml:"name"`
	Ipam Ipam   `yaml:"ipam"`
}
type Ipam struct {
	Config []Config `yaml:"config"`
}

type Config struct {
	Subnet  string `yaml:"subnet"`
	Gateway string `yaml:"gateway"`
}

type Service struct {
	Labels        []string             `yaml:"labels,omitempty"`
	ContainerName string               `yaml:"container_name,omitempty"`
	Image         string               `yaml:"image"`
	Logging       Logging              `yaml:"logging,omitempty"`
	Command       string               `yaml:"command,omitempty"`
	Healthcheck   Healthcheck          `yaml:"healthcheck,omitempty"`
	Environment   []string             `yaml:"environment,omitempty"`
	Volumes       []string             `yaml:"volumes,omitempty"`
	DependsOn     map[string]Condition `yaml:"depends_on,omitempty"`
}

type Logging struct {
	Driver string `yaml:"driver"`
}
type Healthcheck struct {
	Interval string   `yaml:"interval"`
	Retries  int      `yaml:"retries"`
	Test     []string `yaml:"test"`
	Timeout  string   `yaml:"timeout"`
}

type Condition struct {
	Condition string `yaml:"condition"`
}
