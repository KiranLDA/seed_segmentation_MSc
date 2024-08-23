// POD = 0
// SEED = 1
// INTERIOR = 2
// ENDOSPERM = 3
// INFESTATION = 4
// VOID = 5


function calculateNumberOfSeeds(data) {
    return data.response.seed_indices.length;
}

function getSeedIndexes(data) {
    return data.response.annotations.flatMap((annotation, index) => 
        annotation.label === 1 ? index : []
    );
}

function countMaskLabels(data) {
    let annotationEnumMap = {0: 'POD', 1: 'SEED', 2: 'INTERIOR', 3: 'ENDOSPERM', 4: 'INFESTATION', 5: 'VOID'};
    let annotationCount = {POD: 0, SEED: 0, INTERIOR: 0, ENDOSPERM: 0, INFESTATION: 0, VOID: 0};
    data.response.annotations.forEach((annotation) => {
        annotationCount[annotationEnumMap[annotation.label]]++;
    });
    return annotationCount;
}

function classifier(data) {
    console.log("classifier() triggered");
    let classifications = {};
    let classification_count = {EMPTY: 0, PART: 0, FULL: 0, INFESTED: 0};
    let seed_health_dict = {};

    data.response.seed_indices.forEach((seed_indices) => {
        let classification = null;
        let stats = [0, 0, false]; // inside area, endosperm area, contains infestation
        let seed_idx = {};
        let seed_annotations = seed_indices.map((seed_index) => data.response.annotations[seed_index]);
        seed_annotations.forEach((annotation) => {
            if (annotation.label === 1) {
                seed_idx = annotation.seed_id;
            }
            if (annotation.label !== 1 && annotation.label !== 0) {
                stats[0] += annotation.area;
            }
            if (annotation.label === 3) {
                stats[1] = annotation.area;
            }
            if (annotation.label === 4) {
                stats[2] = true;
            }
        });

        let seed_health = stats[1] / stats[0];

        if (stats[2]) {
            classification = "INFESTED";
        } else {
            
            if (seed_health >= data.thresholds.high) {
                classification = "FULL";
            } else if (seed_health < data.thresholds.low) {
                classification = "EMPTY";
            } else {
                classification = "PART";
            }
        }
        classifications[seed_idx] = classification;
        if (seed_health === 1) {
            seed_health = 0.999;
        }
        seed_health_dict[seed_idx] = seed_health.toFixed(3);
    });

    for (let seed_id in classifications) {
        classification_count[classifications[seed_id]]++;
    }
    console.log("classification_count", classification_count);
    return { classifications, classification_count, seed_health_dict };
}


function seedImageLoader(seed_idx, data, callback) {

    let annotations = data.response.annotations.filter((annotation) => annotation.seed_id === seed_idx);

    let image = new Image();
    image.src = data.root_image;
    image.onload = () => {
        let canvas = document.createElement('canvas');
        let ctx = canvas.getContext('2d');
        canvas.width = image.width;
        canvas.height = image.height;
        ctx.drawImage(image, 0, 0);

        let seed_bbox = annotations.reduce((bbox, annotation) => {
            let x = annotation.bbox[0];
            let y = annotation.bbox[1];
            let width = annotation.bbox[2];
            let height = annotation.bbox[3];
            let right = x + width;
            let bottom = y + height;

            if (x < bbox.x) {
                bbox.x = x;
            }
            if (right > bbox.right) {
                bbox.right = right;
            }
            if (y < bbox.y) {
                bbox.y = y;
            }
            if (bottom > bbox.bottom) {
                bbox.bottom = bottom;
            }
            return bbox;
        }, { x: Infinity, right: 0, y: Infinity, bottom: 0 });
        seed_bbox.width = seed_bbox.right - seed_bbox.x;
        seed_bbox.height = seed_bbox.bottom - seed_bbox.y;

        let padding = 0.5;
        seed_bbox.x = seed_bbox.x - seed_bbox.width * padding;
        seed_bbox.y = seed_bbox.y - seed_bbox.height * padding;
        seed_bbox.width = seed_bbox.width * (1 + 2 * padding);
        seed_bbox.height = seed_bbox.height * (1 + 2 * padding);

        let seed_image = document.createElement('canvas');
        let seed_image_ctx = seed_image.getContext('2d');
        seed_image.width = seed_bbox.width;
        seed_image.height = seed_bbox.height;
        seed_image_ctx.drawImage(image, seed_bbox.x, seed_bbox.y, seed_bbox.width, seed_bbox.height, 0, 0, seed_bbox.width, seed_bbox.height);
        
        callback(seed_image.toDataURL());
    }
}

function seedMaskLoader(mask_idx, seed_idx, data, callback) {

    console.log("seedMaskLoader() triggered");

    let annotations = data.response.annotations.filter((annotation) => annotation.seed_id === seed_idx);
    let mask_annotation = annotations.find(annotation => annotation.label === mask_idx);

    if (!mask_annotation) {
        callback(false);
        return;
    }

    let maskImage = new Image();
    maskImage.src = 'data:image/png;base64,' + mask_annotation.mask;
    maskImage.onload = () => {
        let canvas = document.createElement('canvas');
        let ctx = canvas.getContext('2d');
        canvas.width = maskImage.width;
        canvas.height = maskImage.height;
        ctx.drawImage(maskImage, 0, 0);

        let seed_bbox = annotations.reduce((bbox, annotation) => {
            let x = annotation.bbox[0];
            let y = annotation.bbox[1];
            let width = annotation.bbox[2];
            let height = annotation.bbox[3];
            let right = x + width;
            let bottom = y + height;

            if (x < bbox.x) {
                bbox.x = x;
            }
            if (right > bbox.right) {
                bbox.right = right;
            }
            if (y < bbox.y) {
                bbox.y = y;
            }
            if (bottom > bbox.bottom) {
                bbox.bottom = bottom;
            }
            return bbox;
        }, { x: Infinity, right: 0, y: Infinity, bottom: 0 });
        seed_bbox.width = seed_bbox.right - seed_bbox.x;
        seed_bbox.height = seed_bbox.bottom - seed_bbox.y;

        let padding = 0.5;
        seed_bbox.x = seed_bbox.x - seed_bbox.width * padding;
        seed_bbox.y = seed_bbox.y - seed_bbox.height * padding;
        seed_bbox.width = seed_bbox.width * (1 + 2 * padding);
        seed_bbox.height = seed_bbox.height * (1 + 2 * padding);

        let mask_image = document.createElement('canvas');
        let mask_image_ctx = mask_image.getContext('2d');
        mask_image.width = seed_bbox.width;
        mask_image.height = seed_bbox.height;
        mask_image_ctx.drawImage(maskImage, seed_bbox.x, seed_bbox.y, seed_bbox.width, seed_bbox.height, 0, 0, seed_bbox.width, seed_bbox.height);
        
        let imageData = mask_image_ctx.getImageData(0, 0, mask_image.width, mask_image.height);
        let data = imageData.data;

        for (let i = 0; i < data.length; i += 4) {
            if (data[i] === 255) { // mask pixel
                switch (mask_idx) {
                    case 1: // SEED
                        data[i] = 128; // purple
                        data[i + 1] = 0; // green
                        data[i + 2] = 128; // blue
                        break;
                    case 2: // INTERIOR
                        data[i] = 0; // red
                        data[i + 1] = 0; // green
                        data[i + 2] = 255; // blue
                        break;
                    case 3: // ENDOSPERM
                        data[i] = 0; // red
                        data[i + 1] = 128; // green
                        data[i + 2] = 0; // blue
                        break;
                    case 4: // INFESTATION
                        data[i] = 255; // red
                        data[i + 1] = 0; // green
                        data[i + 2] = 0; // blue
                        break;
                    case 5: // VOID
                        data[i] = 255; // red
                        data[i + 1] = 165; // orange
                        data[i + 2] = 0; // blue
                        break;
                    case 0: // POD
                    default:
                        data[i] = 64; // turquoise
                        data[i + 1] = 224; // turquoise
                        data[i + 2] = 208; // turquoise
                        break;
                }
                data[i + 3] = 127; // 50% opacity
            } else {
                data[i + 3] = 0; // make background transparent
            }
        }

        mask_image_ctx.putImageData(imageData, 0, 0);
        callback(mask_image.toDataURL());
    }
}


function seedClassificationLoader(classification_idx, data, callback) {

    console.log("[", classification_idx, "] seedClassificationLoader() triggered");

    let seed_indices = data.response.seed_indices.filter((seed_indices) => {
        let seed_index = seed_indices.find((seed_index) => data.response.annotations[seed_index].label === 1);
        return data.classifications[data.response.annotations[seed_index].seed_id] === classification_idx;
    });

    let annotations = seed_indices.flatMap((seed_indices) => {
        return seed_indices.map((seed_index) => data.response.annotations[seed_index]);
    });

    let image = new Image();
    image.src = data.root_image;
    image.onload = () => {
        let canvas = document.createElement('canvas');
        let ctx = canvas.getContext('2d');
        canvas.width = image.width;
        canvas.height = image.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        let maskImages = annotations.map((annotation) => {
            let maskImage = new Image();
            maskImage.src = 'data:image/png;base64,' + annotation.mask;
            return maskImage;
        });

        Promise.all(maskImages.map(maskImage => new Promise((resolve, reject) => {
            maskImage.onload = () => {
                let maskCanvas = document.createElement('canvas');
                let maskCtx = maskCanvas.getContext('2d');
                maskCanvas.width = image.width;
                maskCanvas.height = image.height;
                maskCtx.drawImage(maskImage, 0, 0);
                ctx.drawImage(maskCanvas, 0, 0);
                resolve();
            };
            maskImage.onerror = reject;
        }))).then(() => {
            let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            let data = imageData.data;

            for (let i = 0; i < data.length; i += 4) {
                if (data[i] === 255) { // mask pixel
                    switch (classification_idx) {
                        case 'FULL':
                            data[i] = 0; // red
                            data[i + 1] = 255; // green
                            data[i + 2] = 0; // blue
                            break;
                        case 'EMPTY':
                            data[i] = 255;
                            data[i + 1] = 255;
                            data[i + 2] = 0;
                            break;
                        case 'PART':
                            data[i] = 0;
                            data[i + 1] = 0;
                            data[i + 2] = 255;
                            break;
                        case 'INFESTED':
                            data[i] = 255;
                            data[i + 1] = 0;
                            data[i + 2] = 0;
                            break;
                        default:
                            data[i+3] = 0;
                    }
                    data[i + 3] = 100; // 50% opacity
                }
            }

            ctx.putImageData(imageData, 0, 0);
            callback(canvas.toDataURL());
        });
    }
    
}





export { calculateNumberOfSeeds, getSeedIndexes, countMaskLabels, classifier, seedImageLoader, seedMaskLoader, seedClassificationLoader };