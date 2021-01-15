{
  description = "Python env needed to run TimesheetLogic";
  # Provides abstraction to boiler-code when specifying multi-platform outputs.
  inputs.flake-utils.url = "github:numtide/flake-utils";
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShell = pkgs.mkShell {
        nativeBuildInputs = [ (pkgs.python38.withPackages(ps: with ps; [ jupyter feedparser beautifulsoup4 ])) ];
      };
    });
}
