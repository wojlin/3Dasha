console.log("xD");

class PrintManager
{
    constructor()
    {
        this.progressBar = document.getElementById("progress_bar");
        this.progressText = document.getElementById("progress_text");
        this.dataFields = document.getElementById("data");

        this.updateProgress(0);

        this.directoryStructure = JSON.parse(this.dataFields.dataset.files);
        this.currentPath = "/";

        this.createDirectory(this.directoryStructure);
    }

    updateProgress(percentage)
    {
        this.progressBar.style.width = percentage.toString() + "%";
        this.progressText.innerHTML = percentage.toString() + "%";
    }

    createDirectory(json)
    {

        if(this.currentPath == "/")
        {
            document.getElementById("directory-return-button").disabled = true;
        }
        else
        {
            document.getElementById("directory-return-button").disabled = false;
        }

        let directoryObj = document.getElementById("directory");
        directoryObj.innerHTML = "";

        console.log(json);


        for (var entry in json)
        {
            let li = document.createElement("li");
            li.classList.add('directory-item');



            let span = document.createElement("span");
            span.classList.add('directory-label');

            if(json[entry] == null)
            {
                li.classList.add('directory-arrow');
                span.classList.add("directory-icon-file");
                span.innerHTML = entry;
                li.setAttribute('data-type', "file");
                li.addEventListener('click', this.highlightFile, false);
                console.log("new file: " + entry);
            }else
            {
                span.classList.add("directory-icon-directory");
                span.innerHTML = entry;
                li.setAttribute('data-type', "directory");
                li.setAttribute('data-structure', JSON.stringify(json[entry]));
                li.setAttribute('data-name', entry);
                li.addEventListener('click', this.updateDirectory, false);
                console.log("new directory: " + entry);
            }



            li.appendChild(span);
            directoryObj.appendChild(li);
        }
    }

    directory_revert()
    {
        let path = this.currentPath.split('/');
        path = path.filter(item => item !== "");
        console.log(path);
        let json = this.directoryStructure;
        let newPath = "/";
        for(var i = 0; i < path.length - 1; i++)
        {
            json = this.directoryStructure[path[i]];
            newPath += path[i] + "/";
        }
        this.currentPath = newPath;
        document.getElementById("directory-path").innerHTML = newPath;
        this.createDirectory(json);
    }

    updateDirectory(element)
    {
        console.log(element.target);

        let id = "selectFilePanel";
        let existingButton = document.getElementById(id);
        if(existingButton != null)
        {
            existingButton.remove();
        }

        let div = document.createElement("div");
        div.id = id;

        let go_button = document.createElement("button");
        go_button.classList.add("directory-selector-button");


        go_button.addEventListener("click", (element) =>
        {
            console.log("clicked element");
            console.log(element.target.parentNode.parentNode)
            let json = JSON.parse(element.target.parentNode.parentNode.dataset.structure);
            let name = element.target.parentNode.parentNode.dataset.name;
            printManager.currentPath += name + "/";
            document.getElementById("directory-path").innerHTML = printManager.currentPath;
            printManager.createDirectory(json);
        });

        //go_button.addEventListener('click', , false, element.target.dataset.structure);
        go_button.innerHTML = "Go Inside";

        let delete_button = document.createElement("button");
        delete_button.classList.add("directory-selector-button");
        delete_button.innerHTML = "Delete";

        div.appendChild(go_button);
        div.appendChild(delete_button);

        element.target.appendChild(div);
    }

    highlightFile(element)
    {
        console.log(element.target);

        let id = "selectFilePanel";
        let existingButton = document.getElementById(id);
        if(existingButton != null)
        {
            existingButton.remove();
        }

        let div = document.createElement("div");
        div.id = id;

        let upload_button = document.createElement("button");
        upload_button.classList.add("directory-selector-button");
        upload_button.innerHTML = "Upload";

        let delete_button = document.createElement("button");
        delete_button.classList.add("directory-selector-button");
        delete_button.innerHTML = "Delete";

        div.appendChild(upload_button);
        div.appendChild(delete_button);

        element.target.appendChild(div);
    }
}

const printManager = new PrintManager();

