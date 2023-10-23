class API
{
    constructor(host, port)
    {
        this.host = host;
        this.port = port;
        this.printer = document.getElementById("data").dataset.printer;
        this.urlBase = "http://" + this.host + ":" + this.port + "/";
    }

    passResponse(value)
    {
        console.log(value)
    }

    setBedTemperature(temperature)
    {
        let url = this.urlBase + "setBedTemperature?printer=" + this.printer + "&temperature=" + temperature;
        this.get(url, api.passResponse);
    }

    setExtruderTemperature(temperature)
    {
        let url = this.urlBase + "setExtruderTemperature?printer=" + this.printer + "&temperature=" + temperature;
        this.get(url, api.passResponse);
    }


    uploadFile(fileName, path)
    {
        let url = this.urlBase + "uploadFile?directoryName=" + fileName + "&directoryPath=" + path;
        this.get(url, printManager.fileUploaded);
    }

    deleteFile(fileName, path)
    {
        let url = this.urlBase + "deleteFile?directoryName=" + fileName + "&directoryPath=" + path;
        this.get(url, printManager.fileDeleted);
    }

    createNewDirectory(directoryName, path)
    {
        let url = this.urlBase + "createNewDirectory?printer=" + this.printer + "&directoryName=" + directoryName + "&directoryPath=" + path;
        this.get(url, printManager.directoryCreated);
    }

    get(url, callback)
    {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function()
        {
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            {
                callback(xmlHttp.responseText);
            }
        }
        console.log(url);
        xmlHttp.open("GET", url, true);
        xmlHttp.send(null);
    }



}

const api = new API("localhost", 5000);