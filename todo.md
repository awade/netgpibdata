AGmeasure
---------
- Implement TFs
- Fix dual channel spectra
- Writing instrument parameters to header
- Detect sweep end instead of waiting; currently does not always get the requested number of averages...

Overall
-------
- Implement a clean command line syntax
    - i.e. "SRmeasure -i vanna -a 10 -f out.txt"
    - Use unified method interface in instrument classes, like old netgpib
