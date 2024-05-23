$(function(){
    // auto-upload on file input change.
    $(document).on('change','.upload-file-aws-s3', function(event){
        var selectedFiles = $(this).prop('files');
        var replace_video_id = $("#replace-video-id").val()

        formItem = $(this).parent()
        $.each(selectedFiles, function(index, item){
            fileItem = verifyFileFormat(item)
            if (fileItem){
                // s3upload = new S3MultiUpload();
                s3upload.start(fileItem, replace_video_id)
            } else {
                alert("Some files are invalid uploads.")
            }
        })
        $(this).val('');

    });
})

function verifyFileFormat(file){
    // verifies the file extension is one we support.
    var extension = file.name.split('.').pop().toLowerCase();
    switch(extension) {
        case 'jpg':
        case 'png':
        case 'gif':
        case 'jpeg':
            return file
        case 'mov':
        case 'mp4':
          return file
        case 'mpeg4':
        case 'avi':
            return file
        case 'mp3':
            return file
        case 'mkv':
            return file
        default:
            notAllowedFiles.push(file)
            return null
    }
};



function S3MultiUpload(){

    this.s3;

    this.partNum = 0;
    this.partSize = 1024 * 1024 * 5;
    this.numPartsLeft = 0;

    this.maxUploadTries = 3;
    this.multiPartParams;
    this.multipartMap;
    this.bucket;
    this.startTime;

    this.byterate = [];
    this.lastUploadedSize = [];
    this.lastUploadedTime = [];
    this.loaded = [];
    this.total = [];
    this.fileItemList = [];
    this.totalLoded = 0;
};

var s3upload = new S3MultiUpload();

s3upload.start = function(fileItem, replaceVideoId) {
    var newLoadingItem;
    s3upload.fileItem = fileItem
    // get AWS upload policy for each file uploaded through the POST method
    // Remember we're creating an instance in the backend so using POST is
    // needed.
    $.ajax({
        method:"POST",
        data: {
            filename: fileItem.name,
            replace_video_id: replaceVideoId,
            university: $("#session-university").val(),
        },
        url: "/api/files/policy/",
        success: function(data){
                policyData = data
        },
        error: function(data){
            alert("An error occured, please try again later")
        }
    }).done(function(){

        numPartsLeft = Math.ceil(fileItem.size / s3upload.partSize);
        s3upload.policyData = policyData
        fileKey = policyData.file_bucket_path;
        bucket = policyData.bucket
        startTime = new Date();

        AWS.config = new AWS.Config();
        AWS.config.update({
            acl: 'public-read',
            accessKeyId: policyData.key,
            filename: policyData.filename,
            Policy: policyData.policy,
            Signature: policyData.signature,

            accessKeyId: policyData.accessKey,
            secretAccessKey: policyData.secretKey,
        }); // for simplicity. In prod, use loadConfigFromFile, or env variables

        s3 = new AWS.S3({signatureVersion: 'v4'});
        // s3.config.update(config)

        multiPartParams = {

            Bucket: bucket,
            Key: policyData.file_bucket_path,
            ContentType: fileItem.type != '' ? fileItem.type : 'application/octet-stream'
        };
        multipartMap = {
            Parts: []
        };

        // Multipart
        s3.createMultipartUpload(multiPartParams, function(mpErr, multipart){
          if (mpErr) { console.log('Error!', mpErr); return; }
          console.log("Got upload ID");

          // Grab each partSize chunk and upload it as a part
          for (var rangeStart = 0; rangeStart < fileItem.size; rangeStart += s3upload.partSize) {

            s3upload.partNum++;
            var end = Math.min(rangeStart + s3upload.partSize, fileItem.size),
            partParams = {
                Body: fileItem.slice(rangeStart, end),
                Bucket: bucket,
                Key: fileKey,
                PartNumber: String(s3upload.partNum),
                UploadId: multipart.UploadId
            };

            // Send a single part

            console.log('Uploading part: #', partParams.PartNumber, ', Range start:', rangeStart);
            s3upload.uploadPart(s3, multipart, partParams);
          }
        });

    })
}

s3upload.fileUploadComplete = function(fileItem, policyData){
    data = {
        uploaded: true,
        fileSize: fileItem.size,
        file: policyData.file_id,
        obj_id: $("#obj_id").val(),
        obj_type: $("#obj_type").val(),

    }
    $.ajax({
        method:"POST",
        data: data,
        url: "/api/files/complete/",
        success: function(data){
            uploaded_file_id = data.id
            s3upload.displayItems(s3upload.fileItemList)
            contentUid = $("#obj_id").val() || undefined
            s3upload.fileItemList.splice( $.inArray(fileItem, s3upload.fileItemList), 1 );
            setTimeout(function(){ stateChange(contentUid) }, 2000);

        },
        error: function(jqXHR, textStatus, errorThrown){
            alert("An error occured, please refresh the page.")
        }
    })
}

s3upload.displayItems = function(fileItemList){
    var itemList = $('.item-loading-queue')
    itemList.html("")
    $.each(fileItemList, function(index, obj){
        var item = obj.file
        var id_ = obj.id
        var order_ = obj.order
        var html_ = "<div id=\"progress_bar\" class=\"progress\">" +
          "<div class=\"progress-bar bg-success\" role=\"progressbar\" style='width:" + item.progress + "%' aria-valuenow='" + item.progress + "' aria-valuemin=\"0\" aria-valuemax=\"100\"></div></div>"
        itemList.append("<div>" + item.name + "<br/>" + html_ + "</div><hr/>")

    })
}

s3upload.getReadableFileSizeString = function(fileSizeInBytes) {
    var i = -1;
    var byteUnits = [' KB', ' MB', ' GB', ' TB', 'PB', 'EB', 'ZB', 'YB'];
    do {
        fileSizeInBytes = fileSizeInBytes / 1024;
        i++;
    } while (fileSizeInBytes > 1024);

    return Math.max(fileSizeInBytes, 0.1).toFixed(1) + byteUnits[i];
}
function addList(total, num) {
  return total + num;
}
s3upload.updateProgress = function() {
    var total=0;
    var loaded=0;
    var byterate=0.0;
    var values = Object.keys(s3upload.loaded).map(function (key) { return s3upload.loaded[key]; });
    for (var i=0; i<s3upload.total.length; ++i) {
        loaded += +s3upload.loaded[i] || 0;
        total += s3upload.total[i];
        if (s3upload.loaded[i]!=s3upload.total[i])
        {
            // Only count byterate for active transfers
            byterate += +s3upload.byterate[i] || 0;
        }
    }
    total=s3upload.fileItem.size;
    s3upload.onProgressChanged(values.reduce(addList, 0), total, byterate);
};

s3upload.onProgressChanged = function(uploadedSize, totalSize, speed) {
        var progress = parseInt(uploadedSize / totalSize * 100, 10);
        var itemList = $('.item-loading-queue')
        itemList.html("")

        var html_ = "<div id=\"progress_bar\" class=\"progress\">" +
          "<div class=\"progress-bar bg-success\" role=\"progressbar\" style='width:" + progress
          + "%' aria-valuenow='" + progress + "' aria-valuemin=\"0\" aria-valuemax=\"100\">"
          + s3upload.getReadableFileSizeString(uploadedSize)+" / "+s3upload.getReadableFileSizeString(totalSize)
            + " <span style='font-size:smaller;color:#000000;'>("
            +uploadedSize+" / "+totalSize
            +" at "
            +s3upload.getReadableFileSizeString(speed)+"ps"
            +")</span></div></div>"
        itemList.append("<div class='pt-3'>" + s3upload.fileItem.name + "<br/>" + html_ + "</div><hr/>")

    };

s3upload.completeMultipartUpload = function(s3, doneParams) {
    s3.completeMultipartUpload(doneParams, function(err, data) {
        if (err) {
            console.log("An error occurred while completing the multipart upload");
            console.log(err);
        } else {
            var delta = (new Date() - startTime) / 1000;
            s3upload.fileUploadComplete(s3upload.fileItem, s3upload.policyData)
        }
  });
}

s3upload.uploadPart =  function(s3, multipart, partParams, tryNum) {
    var tryNum = tryNum || 1;
    s3.uploadPart(partParams, function(multiErr, mData) {
        if (multiErr){
            console.log('multiErr, upload part error:', multiErr);
            if (tryNum < s3upload.maxUploadTries) {
                console.log('Retrying upload of part: #', partParams.PartNumber)
                s3upload.uploadPart(s3, multipart, partParams, tryNum + 1);
            } else {
                console.log('Failed uploading part: #', partParams.PartNumber)
            }
            return;
        }
        multipartMap.Parts[this.request.params.PartNumber - 1] = {
            ETag: mData.ETag,
            PartNumber: Number(this.request.params.PartNumber)
        };
        console.log("Completed part", this.request.params.PartNumber);

        if (--numPartsLeft > 0) return; // complete only when all parts uploaded

        var doneParams = {
            Bucket: bucket,
            Key: fileKey,
            MultipartUpload: multipartMap,
            UploadId: multipart.UploadId
        };

        console.log("Completing upload...");
        s3upload.completeMultipartUpload(s3, doneParams);
    }).on('httpUploadProgress', function(progress, response) {
        if (progress.lengthComputable) {
            partNum = response.request.params.PartNumber
            s3upload.total[partNum] = multipart.size;
            s3upload.loaded[partNum] = progress.loaded;
            if (s3upload.lastUploadedTime[partNum])
            {
                var time_diff=(new Date().getTime() - s3upload.lastUploadedTime[partNum])/1000;
                if (time_diff > 0.005) // 5 miliseconds has passed
                {
                    var byte_rate = (s3upload.loaded[partNum] -s3upload.lastUploadedSize[partNum])/time_diff;
                    s3upload.byterate[s3upload.partNum] = byte_rate;
                    s3upload.lastUploadedTime[partNum]=new Date().getTime();
                    s3upload.lastUploadedSize[partNum]=s3upload.loaded[partNum];
                }
            }
            else
            {
                s3upload.byterate[partNum] = 0;
                s3upload.lastUploadedTime[partNum]=new Date().getTime();
                s3upload.lastUploadedSize[partNum]=s3upload.loaded[partNum];
            }
            // Only send update to user once, regardless of how many
            // parallel XHRs we have (unless the first one is over).
            if (partNum==0 || s3upload.total[0]==s3upload.loaded[0])
                s3upload.updateProgress();
        }
        // Here you can use `this.body` to determine which file this particular
        // event is related to and use that info to calculate overall progress.
    });
}
