while true; do
    read -p "Have you checked http://raiders2:7732/#/search/ isn't already running ?" yn
    case $yn in
        [Yy]* ) echo 'You may have the error request timeout while loading the page. Please wait a few minutes and reload the page.'; export PATH=/lfs/raiders2/0/tpalo/local/bin/:$PATH; export ES_HEAP_SIZE=25g; PORT=7732 mindbender search gui;;
        [Nn]* ) echo 'Please check'; exit;;
        * ) echo "Please answer y or n.";;
    esac
done
echo 

#echo 'maintenance of the views right now, should be back working in a few hours'

#You may have a request timeout while launching it. Just wait a few minutes and reload the page
