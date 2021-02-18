
google.charts.load('current', {'packages':['corechart'], 'language':'ko'});

let start_date;
let end_date;
let music_list;
let selected_music_id_set = new Set();

function search(music_list, id) {
    for (index in music_list) {
        let music = music_list[index];
        if (id == music["id"]) {
            return music;
        }
    }
    return undefined;
}

function displayMusicDefault(music) {
    let artist_list = music["artist"];
    let genre_list = new Set();
    for (index in artist_list) {
        let artist = artist_list[index];
        for (genre_index in artist["genre"]) {
            let genre = artist["genre"][genre_index];
            genre_list.add(genre);
        }
    }

    $(".album-img").attr("src", music["album"]["image_src"]);
    $(".album-name").text(music["album"]["type"] + " " + music["album"]["name"]);
    $(".music-name").text(music["name"]);
    $(".artist-name").text($.map(music["artist"], function(v) { return v.name }).join(", "));
    $(".music-genre").text($.map(music["genre"], function(v) { return v }).join(", "));
    $(".album-genre").text($.map(music["album"]["genre"], function(v) { return v }).join(", "));
    $(".artist-genre").text(Array.from(genre_list).join(", "));
    $(".artist-type").text($.map(music["artist"], function(v) { return v["type"]; }).join(", "));
    $(".release_date").text(music["release_date"].substring(0, 10));
}

function dateToString(date) {
    let mm = date.getMonth() + 1;
    let dd = date.getDate();
    let h = date.getHours();

    yymmdd = [
        date.getFullYear(),
        (mm > 9 ? '' : '0') + mm,
        (dd > 9 ? '' : '0') + dd
    ].join("-");

    hms = [
        (h > 9 ? '' : '0') + h,
        '00',
        '00'
    ].join(":");

    return yymmdd + " " + hms;
}

function drawChart(selected_music_id_set) {
    let header = new Array('날짜');
    let ranking_map = {};

    let temp_start_date = new Date(start_date + " 00:00:00");
    let temp_end_date = new Date(end_date + " 23:00:00");
    let cur_date = temp_start_date;
    while (cur_date <= temp_end_date) {
        str_cur_date = dateToString(cur_date);
        ranking_map[str_cur_date] = [str_cur_date];
        cur_date.setTime(cur_date.getTime() + (1*60*60*1000));
    }

    let count = 0;
    for (id of selected_music_id_set) {
        count += 1;
        let music = search(music_list, id);
        header.push(music["name"]);
        let ranking_list = music["ranking"];
        for (ranking of ranking_list) {
            let date = ranking["date"];
            let rank = ranking["rank"];
            ranking_map[date].push(rank);
        }
        for (key in ranking_map) {
            let ranking = ranking_map[key];
            if (ranking.length <= count) {
                ranking.push(null);
            }
        }
    }

    var data = new google.visualization.DataTable();
    for (index in header) {
        if (index == 0) {
            data.addColumn("datetime", header[index]);
        }
        else {
            data.addColumn("number", header[index]);
        }
    }
    for (key in ranking_map) {
        let ranking = ranking_map[key];
        ranking[0] = new Date(ranking[0]);
        data.addRow(ranking);
    }

    var options = {
        title: 'Melon 랭킹 (실시간)',
        curveType: 'function',
        legend: { position: 'bottom' },
        height: 500,
        vAxis: {
            viewWindowMode: 'explicit',
            viewWindow: {
                min: 0
            },
            direction: '-1'
        },
        hAxis : {
            format : 'dd'
        }
    };

    var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

    chart.draw(data, options);
}

function clickCheckbox(e) {
    if (this.checked == true) {
        $("#music_" + this.value).css("background-color", "skyblue");
        selected_music_id_set.add(Number(this.value));
    }
    else {
        $("#music_" + this.value).css("background", "none");
        selected_music_id_set.delete(Number(this.value));
    }
    let music = search(music_list, this.value);
    displayMusicDefault(music);
    $(".num-selected").text("#: " + selected_music_id_set.size + " / " + music_list.length)
    drawChart(selected_music_id_set);
}

function initMusicList(music_list) {
    let div_music_list = $(".music-list");

    $(".num-selected").text("#: " + "0 / " + music_list.length)

    for (index in music_list) {
        let music = music_list[index];

        let label = document.createElement("label");
        label.className = "music-short-info flex-row";
        label.id = "music_" + music["id"];

        let figure = document.createElement("figure");
        let img = document.createElement("img");
        img.src = music["album"]["image_src"];
        img.alt = "";

        figure.append(img)

        let div = document.createElement("div");
        div.className = "flex-col";

        let span_title = document.createElement("span");
        let span_artist = document.createElement("span");
        span_title.textContent = music["name"]
        span_artist.textContent = $.map(music["artist"], function(v) {
            return v.name;
        }).join(", ");

        div.append(span_title);
        div.append(span_artist);

        let input = document.createElement("input");
        input.type = "checkbox";
        input.name = "music-checkbox";
        input.value = music["id"];
        input.onclick = clickCheckbox;

        label.append(figure);
        label.append(div);
        label.append(input);

        div_music_list.append(label);
    }
}

function filterApply(e) {
    let filter_music_list = new Set();

    let N_min = $("input[name='min'").val();
    let N_max = $("input[name='max'").val();

    let genre_list = $("input[name='genre'");
    let type_list = $("input[name='type']");
    let artist_list = $(".div-a-name > span");
    let album_list = $(".div-al-name > span");

    for (music of music_list) {
        let is_selected_ranking = false;
        let is_selected_genre = true;
        let is_selected_type = true;
        let is_selected_artist = true;
        let is_selected_album = true;

        for (ranking of music["ranking"]) {
            if (N_min <= ranking["rank"] && ranking["rank"] <= N_max) {
                is_selected_ranking = true;
                break;
            }
        }

        for (index = 0; index < genre_list.length; index++) {
            genre = genre_list[index];
            if (genre.checked == true) {
                is_selected_genre = false;
                if (music["genre"].indexOf(genre.value) != -1) {
                    is_selected_genre = true;
                    break;
                }
                for (artist of music["artist"]) {
                    if (artist["genre"].indexOf(genre.value) != -1) {
                        is_selected_genre = true;
                        break;
                    }
                }
                if (is_selected_genre == true) {
                    break;
                }
                if (music["album"]["genre"].indexOf(genre.value) != -1) {
                    is_selected_genre = true;
                    break;
                }
            }
        }

        for (index = 0; index < type_list.length; index++) {
            type = type_list[index];
            if (type.checked == true) {
                is_selected_type = false;
                for (artist of music["artist"]) {
                    if (artist["type"].indexOf(type.value) != -1) {
                        is_selected_type = true;
                        break;
                    }
                }
                if (is_selected_type == true) {
                    break;
                }
            }
        }

        for (index = 0; index < artist_list.length; index++) {
            is_selected_artist = false;
            artist = artist_list[index];
            artist_id = Number(artist.id.split("_")[1]);
            for (artist of music["artist"]) {
                if (artist["id"] == artist_id) {
                    console.log(artist["name"]);
                    is_selected_artist = true;
                    break;
                }
            }
            if (is_selected_artist == true) {
                break;
            }
        }

        for (index = 0; index < album_list.length; index++) {
            is_selected_album = false;
            album = album_list[index];
            album_id = Number(album.id.split("_")[1]);
            if (music["album"]["id"] == album_id) {
                is_selected_album = true;
                break;
            }
        }

        if (is_selected_ranking && is_selected_genre && is_selected_type && is_selected_artist && is_selected_album) {
            filter_music_list.add(music["id"]);
        }
    }

    for (music of filter_music_list) {
        let check = $("input[value='" + music + "']");
        check.prop("checked", true);
        $("#music_" + music).css("background-color", "skyblue");
        selected_music_id_set.add(music);
    }
    $(".num-selected").text("#: " + selected_music_id_set.size + " / " + music_list.length)
    drawChart(selected_music_id_set);
}

function filterInit(e) {
    $("input[name='genre']").prop("checked", false);
    $("input[name='type']").prop("checked", false);

    $(".div-aal-name").remove();
    
    $("input[name='music-checkbox']").prop("checked", false);
    selected_music_id_set = new Set();
    $(".music-short-info").css("background", "none");
    $(".num-selected").text("#: " + selected_music_id_set.size + " / " + music_list.length)
    drawChart(selected_music_id_set);
}

function initMusicListFilter(music_list) {
    let div_filter_genre = $(".filter-genre");
    let div_filter_type =$(".filter-type");
    let datalist_artist = $("#artist-name-list");
    let datalist_album = $("#album-name-list");

    let genre_set = new Set();
    let type_set = new Set();
    let artist_set = new Set();
    let album_set = new Set();

    for (music of music_list) {
        for (genre of music["genre"]) {
            genre_set.add(genre);
        }
        for (genre of music["album"]["genre"]) {
            genre_set.add(genre);
        }
        for (artist of music["artist"]) {
            for (genre of artist["genre"]) {
                genre_set.add(genre);
            }
            for (type of artist["type"]) {
                type_set.add(type);
            }
            artist_set.add(artist["id"] + ", " + artist["name"]);
        }
        album_set.add(music["album"]["id"] + ", " + music["album"]["name"]);
    }

    for (genre of genre_set) {
        let label = document.createElement("label");
        let input = document.createElement("input");
        input.type = "checkbox";
        input.name = "genre";
        input.value = genre;
        label.append(input);
        label.append(genre);
        div_filter_genre.append(label);
    }

    for (type of type_set) {
        let label = document.createElement("label");
        let input = document.createElement("input");
        input.type = "checkbox";
        input.name = "type";
        input.value = type;
        label.append(input);
        label.append(type);
        div_filter_type.append(label);
    }

    $(".input-a-name").keydown(function(key) {
        if (key.keyCode == 13) {
            let div = document.createElement("div");
            div.className = "div-aal-name div-a-name";
            let span = document.createElement("span");
            let del = document.createElement("button");
            span.id = "artist_" + this.value.split(", ")[0];
            span.textContent = this.value;
            del.textContent = "-";
            del.onclick = function(e) {
                div.remove();
            }
            div.append(span);
            div.append(del);

            $(".filter-a-name").append(div);
            this.value = "";
        }
    });

    for (artist of artist_set) {
        let option = document.createElement("option");
        option.value = artist
        datalist_artist.append(option);
    }
    
    $(".input-al-name").keydown(function(key) {
        if (key.keyCode == 13) {
            let div = document.createElement("div");
            div.className = "div-aal-name div-al-name";
            let span = document.createElement("span");
            let del = document.createElement("button");
            span.id = "album_" + this.value.split(", ")[0];
            span.textContent = this.value;
            del.textContent = "-";
            del.onclick = function(e) {
                div.remove();
            }
            div.append(span);
            div.append(del);

            $(".filter-al-name").append(div);
            this.value = "";
        }
    });

    for (album of album_set) {
        let option = document.createElement("option");
        option.value = album
        datalist_album.append(option);
    }

    $("#filter-apply").click(filterApply);
    $("#filter-init").click(filterInit);
}

function drawGenreCountChart(genre_list) {
    let header = new Array("날짜");
    let cnt_list = ["1~10", "11~30", "31~50", "51~70", "71~90", "91~100"];
    let cnt_map = {};

    for (genre of genre_list) {
        header.push(genre.val());
    }

    let temp_start_date = new Date(start_date + " 00:00:00");
    let temp_end_date = new Date(end_date + " 23:00:00");
    let cur_date = temp_start_date;
    while (cur_date <= temp_end_date) {
        str_cur_date = dateToString(cur_date);
        cnt_map[str_cur_date.substring(11, 13)] = [
            [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]
        ];
        cur_date.setTime(cur_date.getTime() + (1*60*60*1000));
    }

    for (i = 0; i < genre_list.length; i++) {
        selected_genre = genre_list[i];
        for (music of music_list) {
            let is_satisfy = false;
            for (genre of music.genre) {
                if (genre == selected_genre.val()) {
                    is_satisfy = true;
                    break;
                }
            }
            if (is_satisfy == false) {
                for (genre of music.album.genre) {
                    if (genre == selected_genre.val()) {
                        is_satisfy = true;
                        break;
                    }
                }
            }
            if (is_satisfy == false) {
                for (artist of music.artist) {
                    for (genre of artist.genre) {
                        if (genre == selected_genre.val()) {
                            is_satisfy = true;
                            break;
                        }
                    }
                    if (is_satisfy == true) {
                        break;
                    }
                }
            }
            if (is_satisfy == false) {
                continue;
            }

            for (ranking of music.ranking) {
                for (j = 0; j < cnt_list.length; j++) {
                    cnt = cnt_list[j];
                    let start_cnt = Number(cnt.split("~")[0]);
                    let end_cnt = Number(cnt.split("~")[1]);
                    if (start_cnt <= ranking.rank && ranking.rank <= end_cnt) {
                        cnt_map[ranking["date"].substring(11, 13)][j][i] += 1;
                    }
                }
            }
        }
    }
    
    for (i = 0; i < 6; i++) {
        var data = new google.visualization.DataTable();
        for (j in header) {
            if (j == 0) {
                data.addColumn("string", header[j]);
            }
            else {
                data.addColumn("number", header[j]);
            }
        }
        
        for (key in cnt_map) {
            cnt = cnt_map[key][i];
            var row = new Array();
            row.push(key + "시");
            row.push(cnt[0]);
            row.push(cnt[1]);
            row.push(cnt[2]);
            data.addRow(row);
        }
        
        var options = {
            title: cnt_list[i],
            legend: { position: 'bottom' },
            hAxis: {title: 'Count',  titleTextStyle: {color: '#333'}},
            vAxis: {minValue: 0}
        };
  
        var chart = new google.visualization.LineChart(document.getElementById("genre_cnt_chart_" + (i+1)));
        chart.draw(data, options);
    }
}

function drawTypeCountChart(type_list) {
    let header = new Array("날짜");
    let cnt_list = ["1~10", "11~30", "31~50", "51~70", "71~90", "91~100"];
    let cnt_map = {};

    for (type of type_list) {
        header.push(type.val());
    }

    let temp_start_date = new Date(start_date + " 00:00:00");
    let temp_end_date = new Date(end_date + " 23:00:00");
    let cur_date = temp_start_date;
    while (cur_date <= temp_end_date) {
        str_cur_date = dateToString(cur_date);
        cnt_map[str_cur_date.substring(11, 13)] = [
            [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]
        ];
        cur_date.setTime(cur_date.getTime() + (1*60*60*1000));
    }

    for (i = 0; i < type_list.length; i++) {
        selected_type = type_list[i];
        for (music of music_list) {
            let is_satisfy = false;
            for (artist of music.artist) {
                for (type of artist.type) {
                    if (type == selected_type.val()) {
                        is_satisfy = true;
                        break;
                    }
                }
            }
            if (is_satisfy == false) {
                continue;
            }

            for (ranking of music.ranking) {
                for (j = 0; j < cnt_list.length; j++) {
                    cnt = cnt_list[j];
                    let start_cnt = Number(cnt.split("~")[0]);
                    let end_cnt = Number(cnt.split("~")[1]);
                    if (start_cnt <= ranking.rank && ranking.rank <= end_cnt) {
                        cnt_map[ranking["date"].substring(11, 13)][j][i] += 1;
                    }
                }
            }
        }
    }

    console.log(cnt_map);
    
    for (i = 0; i < 6; i++) {
        var data = new google.visualization.DataTable();
        for (j in header) {
            if (j == 0) {
                data.addColumn("string", header[j]);
            }
            else {
                data.addColumn("number", header[j]);
            }
        }
        
        for (key in cnt_map) {
            cnt = cnt_map[key][i];
            var row = new Array();
            row.push(key + "시");
            row.push(cnt[0]);
            row.push(cnt[1]);
            row.push(cnt[2]);
            data.addRow(row);
        }
        
        var options = {
            title: cnt_list[i],
            legend: { position: 'bottom' },
            hAxis: {title: 'Count',  titleTextStyle: {color: '#333'}},
            vAxis: {minValue: 0}
        };
  
        var chart = new google.visualization.LineChart(document.getElementById("type_cnt_chart_" + (i+1)));
        chart.draw(data, options);
    }
}

function initGenreCountFilter(music_list) {
    let genre_set = new Set();

    for (music of music_list) {
        for (genre of music.genre) {
            genre_set.add(genre);
        }
        for (artist of music.artist) {
            for (genre of artist.genre) {
                genre_set.add(genre);
            }
        }
        for (genre of music.album.genre) {
            genre_set.add(genre);
        }
    }

    for (genre of genre_set) {
        let option = document.createElement("option");
        option.value = genre;
        option.textContent = genre;

        $(".genre-cnt").append(option);
    }

    let genre_list = [ $("select[name='genre-cnt-1']"), $("select[name='genre-cnt-2']"), $("select[name='genre-cnt-3']") ];

    for (genre of genre_list) {
        genre.change(function() {
            drawGenreCountChart(genre_list)
        });
    }
}

function initTypeCountFilter(music_list) {
    let type_set = new Set();

    for (music of music_list) {
        for (artist of music.artist) {
            for (type of artist.type) {
                type_set.add(type);
            }
        }
    }

    for (type of type_set) {
        let option = document.createElement("option");
        option.value = type;
        option.textContent = type;

        $(".type-cnt").append(option);
    }

    let type_list = [ $("select[name='type-cnt-1']"), $("select[name='type-cnt-2']"), $("select[name='type-cnt-3']") ];

    for (type of type_list) {
        type.change(function() {
            drawTypeCountChart(type_list)
        });
    }
}

$(document).ready(function() {
    start_date = $("input[name=startDate]").val();
    end_date = $("input[name=endDate]").val();
    const params = "?startDate=" + start_date + "&endDate=" + end_date;

    let request = new XMLHttpRequest();
    request.open("GET", "json/music.json" + params, true);
    request.responseType = "json";
    request.send();

    request.onload = function() {
        const json_music = request.response;
        music_list = json_music["music_list"];
        initMusicList(music_list);
        initMusicListFilter(music_list);
        initGenreCountFilter(music_list);
        initTypeCountFilter(music_list);
    }
});