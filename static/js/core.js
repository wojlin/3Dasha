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
        this.currentExtrude = 1;
        this.changeExtrude(1, document.getElementById("extrude_1"));

        this.createDirectory(this.directoryStructure);
        this.initMoveButtons();

        this.print_status_file = document.getElementById("print_status_file");
        this.print_status_timelapse = document.getElementById("print_status_timelapse");
        this.print_status_time = document.getElementById("print_status_time");
        this.print_status_time_left = document.getElementById("print_status_time_left");
        this.print_status_printed = document.getElementById("print_status_printed");

        this.print_status_button_print = document.getElementById("print_status_button_print");
        this.print_status_button_pause = document.getElementById("print_status_button_pause");
        this.print_status_button_stop = document.getElementById("print_status_button_stop");

        this.printer_info_name = document.getElementById("printer_info_name");
        this.printer_info_port = document.getElementById("printer_info_port");
        this.printer_info_status = document.getElementById("printer_info_status");


        this.updatePrintStatus();
        this.updatePrinterInfo();
    }

    initMoveButtons()
    {

        for(let x = 1; x <= 3; x++)
        {
            document.getElementById('up_' + x.toString()).addEventListener('click', function(event)
            {
                event.preventDefault();
                let value = 0;
                if(x == 1)
                {
                    value = 1;
                }else if(x == 2)
                {
                    value = 10;
                }else
                {
                    value = 100;
                }

                let data = {"x": 0, "y": 0, "z": value};
                api.move(data);
            });

            document.getElementById('down_' + x.toString()).addEventListener('click', function(event)
            {
                event.preventDefault();
                let value = 0;
                if(x == 1)
                {
                    value = 1;
                }else if(x == 2)
                {
                    value = 10;
                }else
                {
                    value = 100;
                }

                let data = {"x": 0, "y": 0, "z": -value};
                api.move(data);
            });

            document.getElementById('forward_' + x.toString()).addEventListener('click', function(event)
            {
                event.preventDefault();
                let value = 0;
                if(x == 1)
                {
                    value = 1;
                }else if(x == 2)
                {
                    value = 10;
                }else
                {
                    value = 100;
                }

                let data = {"x": 0, "y": value, "z":0};
                api.move(data);
            });

            document.getElementById('back_' + x.toString()).addEventListener('click', function(event)
            {
                event.preventDefault();
                let value = 0;
                if(x == 1)
                {
                    value = 1;
                }else if(x == 2)
                {
                    value = 10;
                }else
                {
                    value = 100;
                }

                let data = {"x": 0, "y": -value, "z":0};
                api.move(data);
            });

            document.getElementById('left_' + x.toString()).addEventListener('click', function(event)
            {
                event.preventDefault();
                let value = 0;
                if(x == 1)
                {
                    value = 1;
                }else if(x == 2)
                {
                    value = 10;
                }else
                {
                    value = 100;
                }

                let data = {"x": -value, "y": 0, "z":0};
                api.move(data);
            });

            document.getElementById('right_' + x.toString()).addEventListener('click', function(event)
            {
                event.preventDefault();
                let value = 0;
                if(x == 1)
                {
                    value = 1;
                }else if(x == 2)
                {
                    value = 10;
                }else
                {
                    value = 100;
                }

                let data = {"x": value, "y": 0, "z":0};
                api.move(data);
            });
        }


    }


    updatePrinterInfo()
    {
        let interval = setInterval(function()
        {
            api.fetchPrinterInfo(data);
        },
        1000);
    }

    postUpdatePrinterInfo(response)
    {
        let json = JSON.parse(response);
        printManager.printer_info_name.innerHTML = json["data"]["name"];
        printManager.printer_info_port.innerHTML = json["data"]["port"];
        printManager.printer_info_status.innerHTML = json["data"]["status"];

    }

    updatePrintStatus()
    {
        let interval = setInterval(function()
        {
            api.fetchPrintStatus(data);
        },
        1000);
    }

    postUpdatePrintStatus(response)
    {
        let json = JSON.parse(response);

        printManager.print_status_file.innerHTML = json["data"]["printed_file"];
        printManager.print_status_timelapse.innerHTML = json["data"]["timelapse_time"];
        printManager.print_status_time.innerHTML = json["data"]["print_time"];
        printManager.print_status_time_left .innerHTML = json["data"]["print_time_left"];
        printManager.print_status_printed.innerHTML = json["data"]["printed_kb"];

        printManager.updateProgress(json["data"]["printed_percentage"]);

        if(json["data"]["is_printing"])
        {
            printManager.print_status_button_print.disabled = true;
            printManager.print_status_button_pause.disabled = false;
            printManager.print_status_button_stop.disabled = false;
        }else
        {
            printManager.print_status_button_pause.disabled = true;
            printManager.print_status_button_stop.disabled = true;

            if(json["data"]["is_file_uploaded"])
            {
                printManager.print_status_button_print.disabled = false;
            }else
            {
                printManager.print_status_button_print.disabled = true;
            }


        }

    }

    updateProgress(percentage)
    {
        this.progressBar.style.width = percentage.toString() + "%";
        this.progressText.innerHTML = percentage.toString() + "%";
    }

    changeExtrude(value, obj)
    {
        let objs = document.getElementsByClassName("extruder_select");
        for(let i = 0; i < objs.length; i++)
        {
            objs[i].style.opacity = 1;
        }
        obj.style.opacity = 0.5;
        this.currentExtrude = value;
        console.log("changed extrude to " + this.currentExtrude + "mm");
    }


    extrude()
    {
        api.extrude(this.currentExtrude);
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
            }else
            {
                span.classList.add("directory-icon-directory");
                span.innerHTML = entry;
                li.setAttribute('data-type', "directory");
                li.setAttribute('data-structure', JSON.stringify(json[entry]));
                li.setAttribute('data-name', entry);
                li.addEventListener('click', this.updateDirectory, false);
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

