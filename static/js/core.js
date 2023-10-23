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


        let create = document.createElement("li");
        create.classList.add('directory-item');
        create.id = "create_new_directory";

        let create_span = document.createElement("span");
        create_span.classList.add('directory-label');
        create_span.classList.add("directory-icon-directory");
        create_span.innerHTML = "+ Create New Directory";
        create.addEventListener('click', this.precreateDirectory, false);

        create.appendChild(create_span);
        directoryObj.appendChild(create);

        for (var entry in json)
        {
            let li = document.createElement("li");
            li.classList.add('directory-item');

            li.setAttribute('data-name', entry);


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

    precreateDirectory(e, own=false)
    {

        if(own==false)
        {
            if(e.target.id != "create_new_directory")
            {
                return;
            }
        }

        let new_dir = document.getElementById("create_new_directory");
        new_dir.childNodes[0].remove()

        let container = document.createElement("div");
        container.id = "create_new_directory_container";
        container.classList.add("create_new_directory_container");

        let input = document.createElement("input");
        input.setAttribute('type', 'text');
        input.id = "create_new_directory_input";

        let button_create = document.createElement("button");
        button_create.classList.add("create_new_directory_button");
        button_create.innerHTML = "create";
        button_create.addEventListener('click', printManager.createNewDirectory, false);

        let button_cancel = document.createElement("button");
        button_cancel.classList.add("create_new_directory_button");
        button_cancel.innerHTML = "cancel";
        button_cancel.addEventListener('click', printManager.cancelCreateDirectory, false);

        container.appendChild(input);
        container.appendChild(button_cancel);
        container.appendChild(button_create);


        new_dir.appendChild(container);
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
        if(!element.target.classList.contains("directory-item"))
        {
            return;
        }

        element.stopPropagation();

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
        upload_button.addEventListener('click', printManager.uploadFile, false);

        let delete_button = document.createElement("button");
        delete_button.classList.add("directory-selector-button");
        delete_button.innerHTML = "Delete";
        delete_button.addEventListener('click', printManager.deleteFile, false);

        div.appendChild(upload_button);
        div.appendChild(delete_button);

        element.target.appendChild(div);
    }

    uploadFile(e)
    {
        let obj = e.target;
        let fileName = obj.parentNode.parentNode.dataset.name;
        let path = printManager.currentPath;
        api.uploadFile(fileName, path);
    }

    deleteFile(e)
    {
        let obj = e.target;
        let fileName = obj.parentNode.parentNode.dataset.name;
        let path = printManager.currentPath;
        api.deleteFile(fileName, path);
    }

    createNewDirectory(e)
    {
        let obj = e.target;
        let directoryName = obj.parentNode.firstChild.value;
        let path = printManager.currentPath;
        api.createNewDirectory(directoryName, path);
    }

    cancelCreateDirectory(e)
    {
        console.log("cancel create dir!")

        document.getElementById("create_new_directory_container").remove();
        let create_span = document.createElement("span");
        create_span.classList.add('directory-label');
        create_span.classList.add("directory-icon-directory");
        create_span.innerHTML = "+ Create New Directory";
        document.getElementById("create_new_directory").appendChild(create_span);
    }



    directoryCreated(data)
    {
        alert(data);
    }

    fileDeleted()
    {
        alert("file deleted!");
    }

    fileUploaded()
    {
        alert("file uploaded!");
    }
S
}

const printManager = new PrintManager();

