{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in with pkgs; rec {
        devShells.${system}.default = mkShell {
          name = "dev-shell";
          nativeBuildInputs = [
            git
            curl
            sudo
            vim
            python3
            pipx
            ruff
            uv
            zsh
            openssh
            mcfly
            jq
            yq
            jaq
          ];
        };
      });
}
