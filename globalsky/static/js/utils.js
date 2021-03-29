function success_rate(proposal, date, state) {
  return new Promise((resolve, reject) => {
  var url = `https://observe.lco.global/api/requestgroups/?proposal=${proposal}&created_after=${date}`
  if (state != null){
    url += `&state=${state}`
  }
  $.ajax({
    url: url,
    headers: {'Authorization': 'Token '+localStorage.getItem('token')},
    type:'get',
    dataType:'json',
    success: function(data){
      var num = data['count']
      resolve(num);
    },
    error: function(error){
      console.log(error)
      reject(error)
    }
    })
  })
}

function time_allocation(proposal) {
  return new Promise((resolve, reject) => {
  $.ajax({
    url: `https://observe.lco.global/api/proposals/${proposal}/`,
    headers: {'Authorization': 'Token '+localStorage.getItem('token')},
    type:'get',
    dataType:'json',
    success: function(data){
      var content;
      for (i=0;i<data['timeallocation_set'].length;i++){
        var d = data['timeallocation_set'][i];
        content += "<tr>";
        content += "<td>" + d['semester'] + "</td>";
        content += `<td><progress class='progress is-success mb-0' value='${d['std_time_used']}' max='${d['std_allocation']}'>`;
        content += Number.parseFloat(d['std_time_used']).toFixed(1) + " / " +d['std_allocation'] + "</progress>";
        content += "<span class='is-size-7'>"+Number.parseFloat(d['std_time_used']).toFixed(1) + " / " +d['std_allocation'] + "</span></td>";
        content += "<td>" + aperture_name(d['instrument_type']) + "</td>";
        content += "</tr>";
      }
      resolve(content)
    },
    error: function(error){
      console.log(error)
      reject(error)
    }
    })
  })
}

function time_allocation_all(semester) {
  return new Promise((resolve, reject) => {
  $.ajax({
    url: `https://observe.lco.global/api/proposals/?limit=100`,
    headers: {'Authorization': 'Token '+localStorage.getItem('token')},
    type:'get',
    dataType:'json',
    success: function(data){
      var content = {};
      for (var j=0;j<data['results'].length;j++){
        results = data['results'][j];
        var html ='';
        for (var i=0;i<results['timeallocation_set'].length;i++){
          var d = results['timeallocation_set'][i];
            if (d['semester'] == semester && d['instrument_type'] == "0M4-SCICAM-SBIG"){
              html += `<progress class='progress is-success mb-0' value='${d['std_time_used']}' max='${d['std_allocation']}'>`;
              html += Number.parseFloat(d['std_time_used']).toFixed(1) + " / " +d['std_allocation'] + "</progress>";
              html += "<span class='is-size-7'>"+Number.parseFloat(d['std_time_used']).toFixed(1) + " / " +d['std_allocation'] + "</span>";
            }
          }
          content[results['id']] = html;
      }
      resolve(content)
    },
    error: function(error){
      console.log(error)
      reject(error)
    }
    })
  })
}

function user_requests(proposal) {
  var d = new Date();
  d.setDate(d.getDate() - 7);
  var datestamp = d.toISOString().substr(0,19).replace('T',' ');

  return new Promise((resolve, reject) => {
  $.ajax({
    url: `https://observe.lco.global/api/requestgroups/?proposal=${proposal}&created_after=${datestamp}`,
    headers: {'Authorization': 'Token '+localStorage.getItem('token')},
    type:'get',
    dataType:'json',
    success: function(data){
      var content;
      for (var i=0;i<data['results'].length;i++){
        var d = data['results'][i];
        content += "<tr>";
        content += "<td><a href='https://observe.lco.global/requestgroups/" + d['id'] +"/'>";
        content += d['name'] + "</a></td>";
        content += "<td>" + d['submitter'] + "</td>";
        content += "<td>" + calculate_time_used(d['requests']) + "</td>";
        content += "<td>" + status_icon(d['state']) + "</td>";
        content += "</tr>";
      }
      resolve(content)
    },
    error: function(error){
      console.log(error)
      reject(error)
    }
    })
  })
}

function total_time(proposals, semesters) {
  return new Promise((resolve, reject) => {
  $.ajax({
    url: 'https://observe.lco.global/api/proposals/?active=True&public=True&limit=100',
    headers: {'Authorization': 'Token '+localStorage.getItem('token')},
    type:'get',
    dataType:'json',
    success: function(data){
      var totals = {'total':0,'used':0};
      var used;
      for (var i=0;i<data['results'].length;i++){
        if (proposals.includes(data['results'][i]['id'])){
          for (var j=0;j<data['results'][i]['timeallocation_set'].length;j++){
            var d = data['results'][i]['timeallocation_set'][j];
            if (semesters.includes(d['semester']) && d['instrument_type'] == '0M4-SCICAM-SBIG'){
              totals.total += d['std_allocation'];
              totals.used += d['std_time_used'];
            }
          }
        }
      }
      resolve(totals)
    },
    error: function(error){
      console.log(error)
      reject(error)
    }
    })
  })
}

function calculate_time_used(observations){
  var total = 0;
  for (var i=0;i<observations.length;i++){
    total += observations[i]['duration']
  }
  return Number.parseFloat(total/3600).toFixed(2)
}

function aperture_name(name){
  var telclass = {
      '0M4-SCICAM-SBIG':'0.4 meter',
      '1M0-SCICAM-SINISTRO':'1 meter',
      '2M0-SCICAM-SPECTRAL' : '2 meter' };

  var tel = telclass[name];
  if (tel == undefined){
    return name
  } else {
    return tel
  }
}

function status_icon(state){
  var states = {
    'COMPLETED' : '<span class="icon"><i class="fas fa-check"></i></span>',
    'FAILED'    : '<span class="icon"><i class="fas fa-times"></i></span>',
    'WINDOW_EXPIRED'    : '<span class="icon"><i class="fas fa-times"></i></span>',
    'PENDING'   : '<span class="icon"><i class="far fa-clock"></i></span>',
    'CANCELED'    : '<span class="icon"><i class="fas fa-minus-circle"></i></span>',

  }
  return states[state]
}
