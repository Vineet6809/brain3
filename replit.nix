{ pkgs }: {
  deps = [
    pkgs.nodejs-18_x
    pkgs.yarn
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.tesseract
    pkgs.mongodb
    pkgs.mongodb-tools
    pkgs.libGL
    pkgs.libGLU
    pkgs.xorg.libX11
    pkgs.xorg.libXext
    pkgs.xorg.libXrender
    pkgs.stdenv.cc.cc.lib
  ];

  env = {
    PYTHONBIN = "${pkgs.python311}/bin/python3";
    LANG = "en_US.UTF-8";
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.libGL
      pkgs.libGLU
    ];
  };
}
