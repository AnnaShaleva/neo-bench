module github.com/nspcc-dev/neo-bench

go 1.14

require (
	github.com/Microsoft/go-winio v0.4.14 // indirect
	github.com/Workiva/go-datastructures v1.0.50
	github.com/containerd/containerd v1.4.3 // indirect
	github.com/docker/distribution v2.7.1+incompatible // indirect
	github.com/docker/docker v20.10.3+incompatible
	github.com/docker/go-connections v0.4.0 // indirect
	github.com/docker/go-units v0.4.0 // indirect
	github.com/fatih/color v1.7.0
	github.com/k14s/ytt v0.30.0
	github.com/mailru/easyjson v0.7.1
	github.com/moby/moby v20.10.3+incompatible
	github.com/nspcc-dev/neo-go v0.94.0
	github.com/opencontainers/go-digest v1.0.0-rc1 // indirect
	github.com/opencontainers/image-spec v1.0.1 // indirect
	github.com/spf13/pflag v1.0.5
	github.com/spf13/viper v1.6.1
	github.com/valyala/fasthttp v1.9.0
	go.uber.org/atomic v1.4.0
	go.uber.org/zap v1.10.0
	gopkg.in/yaml.v2 v2.2.4
)

replace github.com/pkg/errors v0.8.1 => github.com/pkg/errors v0.9.1 // see https://github.com/containerd/containerd/issues/4703#issuecomment-736542317
