let
    pkgs = (import (builtins.fetchTarball {
        url = "https://github.com/NixOS/nixpkgs/archive/63dacb46bf939521bdc93981b4cbb7ecb58427a0.zip";
        sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
    }) { });
    stdenv = pkgs.stdenv;
in pkgs.mkShell rec {
    name = "interview";
    shellHook = ''
        source .bashrc
    '';
    buildInputs = (with pkgs; [
        sqlite
        pkgs.bashInteractive
        (pkgs.python3.buildEnv.override {
            ignoreCollisions = true;
            extraLibs = with pkgs.python3.pkgs; [
                # package list: https://search.nixos.org/packages
                # be parsimonious with 3rd party dependencies; better to show off your own code than someone else's
                ipython
                aiohttp
                nose
                # The pandas and matplotlib library are solely for presentation purposes. They are not part of my solution.
                pandas
                matplotlib
            ];
        })
    ]);
}
