console.log("xD");

class PrintManager
{
    constructor()
    {
        this.progressBar = document.getElementById("progress_bar");
        this.progressText = document.getElementById("progress_text");
        this.dataFields = document.getElementById("data");

        this.updateProgress(0);
        this.createDirectory();
    }

    updateProgress(percentage)
    {
        this.progressBar.style.width = percentage.toString() + "%";
        this.progressText.innerHTML = percentage.toString() + "%";
    }

    createDirectory()
    {
        let directoryObj = document.getElementById("directory");
        let directoryData = JSON.parse(this.dataFields.dataset.files);
        console.log(directoryData);


        for (var entry in directoryData)
        {
            let li = document.createElement("li");
            li.classList.add('directory-item');


            let span = document.createElement("span");
            span.classList.add('directory-label');

            if(directoryData[entry] == null)
            {
                li.classList.add('directory-arrow');
                span.classList.add("directory-icon-file");
                span.innerHTML = entry;
                console.log("new file: " + entry);
            }else
            {
                span.classList.add("directory-icon-directory");
                span.innerHTML = entry;
                console.log("new directory: " + entry);
            }

            li.appendChild(span);
            directoryObj.appendChild(li);
        }


    }

    updateDirectory()
    {

    }
}

const printManager = new PrintManager();

