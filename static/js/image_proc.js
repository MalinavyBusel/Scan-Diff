function showTextBoth(name) {
    document.image_inf.im1.value += name
    document.image_inf.im2.value += name
}

function showTextOne(name, pic_num) {
    if (pic_num === '1') {
        document.image_inf.im1.value += name
    } else {
        document.image_inf.im2.value += name
    }
}

function showText(name, pic_num, colour) {
    if (colour === 'green') {
        showTextBoth(name)
    } else {
        showTextOne(name, pic_num)
    }
}

function cleanText() {
    document.image_inf.im1.value = ''
    document.image_inf.im2.value = ''
}
