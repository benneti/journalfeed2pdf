{
  description = "Python env needed to run TimesheetLogic";
  # Provides abstraction to boiler-code when specifying multi-platform outputs.
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShell = pkgs.mkShell {
        nativeBuildInputs = [ (pkgs.python3.withPackages(ps: with ps; [ jupyter jupyterlab feedparser beautifulsoup4 requests python-dateutil pytest xdg-base-dirs ])) ];
      };
    });
}
