// http://127.0.0.1:8000/counter?RH=0.9&dry_size=60e-9&x_slice=26&y_slice=1&days=50&stack_x0=0&stack_x1=1000&stack_x2=-200&stack_y0=0&stack_y1=250&stack_y2=-500&Q0=40&Q1=40&Q2=40&H0=50&H1=50&H2=50&aerosol_type=1&humidify=1&stab1=1&stability_used=1&output=1&wind=3&stacks=1
// http://127.0.0.1:8000/counter?RH=0.9&dry_size=60e-9&x_slice=26&y_slice=1&days=50&stack_x0=0&stack_x1=1000&stack_x2=-200&stack_y0=0&stack_y1=250&stack_y2=-500&Q0=40&Q1=40&Q2=40&H0=50&H1=50&H2=50&aerosol_type=1&humidify=1&stab1=1&stability_used=1&output=4&wind=3&stacks=1
function toTitleCase(str) {
  return str.replace(
    /\w\S*/g,
    function(txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    }
  );
}


function add_option(options, option_id, option_label){
  // document.write(`<option value="" disabled selected>Please choose </option>`);
  // console.log(`<label for = "${option_id}"> ${option_label}: </label>`);
  // console.log(`<select name = "${option_id}" id = "${option_id}" required>`);
  // console.log(`<option value="" disabled selected>Please choose </option>`);
  // for(var i = 0; i < options.length; i++)
  // {
  //   var val = options[i];
  //   // document.write(`<option value = ${i+1}> ${toTitleCase(val.replace(/_/g, ' '))} </option>`);
  //   console.log(`<option value = ${i+1}> ${toTitleCase(val.replace(/_/g, ' '))} </option>`);
  // }
  // console.log("</select> <br>");

  document.write(`<label for = "${option_id}"> ${option_label}: </label>`);
  document.write(`<select name = "${option_id}" id = "${option_id}" required>`);
  document.write(`<option value="" disabled selected>Please choose </option>`);
  for(var i = 0; i < options.length; i++)
  {
    var val = options[i];
    document.write(`<option value = ${i+1}> ${toTitleCase(val.replace(/_/g, ' '))} </option>`);
  }
  document.write("</select> <br>");
}

// <!-- <select name = "aerosol_type" id = "aerosol_type" required> -->
// <!--   <option value="" disabled selected>Please choose </option> -->
// <!--   <option value = "SODIUM_CHLORIDE">Sodium chloride</option> -->
// <!--   <option value = "SULPHURIC_ACID">Sulfuric acid</option> -->
// <!--   <option value = "ORGANIC_ACID">Organic acid</option> -->
// <!--   <option value = "Ammonium nitrate">Sulfuric acid</option> -->
// <!-- </select> <br> -->

// <!-- <label for = "aerosol_type"> Aerosol Type: </label> -->
// <!-- <select name = "aerosol_type" id = "aerosol_type" required> -->
//   <!--   <script language="javascript" type="text/javascript"> -->
//     <!--     // var aerosol_types = {"SODIUM_CHLORIDE": 1, "SULPHURIC_ACID": 2, "ORGANIC_ACID": 3, "AMMONIUM_NITRATE": 4}; -->
//     <!--     var aerosol_types = ["SODIUM_CHLORIDE", "SULPHURIC_ACID", "ORGANIC_ACID", "AMMONIUM_NITRATE"]; -->
//     <!--     document.write(`<option value="" disabled selected>Please choose </option>`); -->
//     <!--     // for(var key in aerosol_types) -->
//     <!--     for(var i = 0; i < aerosol_types.length; i++) -->
//     <!--     { -->
//     <!--       var val = aerosol_types[i]; -->
//     <!--       document.write(`<option value = ${i+1}> ${toTitleCase(val.replace(/_/g, ' '))} </option>`); -->
//     <!--     } -->
//     <!--     </script> -->
//   <!-- </select> <br> -->

// var aerosol_types = ["SODIUM_CHLORIDE", "SULPHURIC_ACID", "ORGANIC_ACID", "AMMONIUM_NITRATE"];
// add_option(aerosol_types, "aerosol_types", "Aerosol Type")
// var aerosol_types = {"SODIUM_CHLORIDE": 1, "SULPHURIC_ACID": 2, "ORGANIC_ACID": 3, "AMMONIUM_NITRATE": 4};
// for(var key in aerosol_types)
// {
//   var val = aerosol_types[key];
//   // console.log(`<option value = ${val}> ${key} </option>`);
//   console.log(`<option value = ${val}> ${toTitleCase(key.replace(/_/g, ' '))} </option>`);
//   // document.write(`<option value = ${val}> ${key} </option>`);
// }


// <!-- <textarea name="text" rows = "10" cols = "100"></textarea> <br> -->
// <!-- <label for = "RH"> RH:  </label> -->
// <!-- <input type = "text" name = "RH" id = "RH" required> <br> -->

// <!-- <label for = "dry_size"> Dry Size:  </label> -->
// <!-- <input type = "text" name = "dry_size" id = "dry_size" required> <br> -->


// var fields = {"RH": "RH", "dry_size": "Dry Size", "x_slice": "Slice id in x-driection (1-50)", "y_slice": "Slice id in y-direction (1-50)", "days": "No. days to run the model"};
// for(var key in fields)
// {
//   var val = fields[key];
//   // console.log(`<option value = ${val}> ${key} </option>`);
//   document.write(`<label for = "${key}"> ${val}:  </label>`);
//   document.write(`<input type = "text" name = "${key}" id = "${key}" required> <br>`);
//   // console.log(`<option value = ${val}> ${toTitleCase(key.replace(/_/g, ' '))} </option>`);
//   // document.write(`<option value = ${val}> ${key} </option>`);
// }



// var aerosol_types = ["SODIUM_CHLORIDE", "SULPHURIC_ACID", "ORGANIC_ACID", "AMMONIUM_NITRATE"];
// console.log(`<option value="" disabled selected>Please choose </option>`);
// // for(var key in aerosol_types)
// for(var i = 0; i < aerosol_types.length; i++)
// {
//   var val = aerosol_types[i];
//   console.log(`<option value = ${i+1}> ${toTitleCase(val.replace(/_/g, ' '))} </option>`);
// }
// // const fruits = new Map([
// //   ["SODIUM_CHLORIDE": 1], ["SULPHURIC_ACID": 2], ["ORGANIC_ACID": 3], ["AMMONIUM_NITRATE": 4]
// //   ["apples", 500],
// //   ["bananas", 300],
// //   ["oranges", 200]
// // ]);

// // for()


// var b  = 3;
// var a = "x" + b - 1;
// console.log(a); // fail
// var c = b - 1;
// var d = "x" + c;
// console.log(d); // success
// function add_stackparams(stack_id){
//   var stack_id_1 = stack_id-1
//   var  fields_p2 = {
//     "stack_x" + stack_id_1: "x-coordinate of stack " +  stack_id, // `${stack_id}`,
//       "stack_y" + stack_id_1: "y-coordinate of stack " +  stack_id,
//       "Q" + stack_id_1: "Mass emitted per unit time of stack " +  stack_id,
//       "H" + stack_id_1: "Height of stack " + stack_id + " (meters)",
//     }

//     for(var key in fields_p2)
//     {
//       var val = fields_p2[key];
//       document.write(`<label for = "${key}"> ${val}:  </label>`);
//       document.write(`<input type = "text" name = "${key}" id = "${key}" required> <br>`);
//     }
// }
// add_stackparams(1)


function add_params(p_id){
  var p_id_1 = p_id-1;
  var  p2s = {};
  //  "stack_x" + p_id_1: "some val " +  p_id
  // }
  p2s["stack_x" + p_id_1] = "some val " +  p_id;

  for(var key in p2s)
  {
    var val = p2s[key];
    console.log(`<label for = "${key}"> ${val}:  </label>`);
    console.log(`<input type = "text" name = "${key}" id = "${key}" required> <br>`);
  }
}
add_params(1);


function add_stackparams(stack_id){
  var stack_id_1 = stack_id-1;
  var  fields_p2 = {};
  fields_p2["stack_x" + stack_id_1] = "x-coordinate of stack " +  stack_id;
  fields_p2["stack_y" + stack_id_1] = "y-coordinate of stack " +  stack_id;
  fields_p2["Q" + stack_id_1] = "Mass emitted per unit time of stack " +  stack_id;
  fields_p2["H" + stack_id_1] = "Height of stack " + stack_id + " (meters)";
  //  "stack_y" + stack_id_1: "y-coordinate of stack " +  stack_id,
  //   "Q" + stack_id_1: "Mass emitted per unit time of stack " +  stack_id,
  //   "H" + stack_id_1: "Height of stack " + stack_id + " (meters)",
  // }

  for(var key in fields_p2)
  {
    var val = fields_p2[key];
    console.log(`<label for = "${key}"> ${val}:  </label>`);
    console.log(`<input type = "text" name = "${key}" id = "${key}" required> <br>`);
  }
}

add_stackparams(1);



// fields_p2 = {
//   "stack_x0": "x-coordinate of stack 1",
//   "stack_y0": "y-coordinate of stack 1",
//   "Q0": "Mass emitted per unit time of stack 1",
//   "H0": "Height of stack 1 (meters)",
// };

// for(var key in fields_p2)
// {
//   var val = fields_p2[key];
//   document.write(`<label for = "${key}"> ${val}:  </label>`);
//   document.write(`<input type = "text" name = "${key}" id = "${key}" required> <br>`);
// }
