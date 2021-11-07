require.config({ paths: { vs: 'static/node_modules/monaco-editor/min/vs' } });

require(['vs/editor/editor.main'], function () {

    monaco.languages.register({
        id: 'hapy'
    });
    monaco.languages.setMonarchTokensProvider('hapy', monarchSettings());

    // Define a new theme that constains only rules that match this language
    monaco.editor.defineTheme('myCoolTheme', {
        base: 'vs',
        inherit: false,
        rules: [
            { token: 'custom-info', foreground: '808080' },
            { token: 'custom-error', foreground: 'ff0000', fontStyle: 'bold' },
            { token: 'custom-notice', foreground: 'FFA500' },
            { token: 'custom-date', foreground: '008800' }
        ]
    });

    window.editor = monaco.editor.create(document.getElementById('container'), {
        value: getCode(),
        language: 'hapy'
    });

    // window.editor = monaco.editor.create(document.getElementById('container'), {
    //     value: getCode(),
    //     language: 'hapy'
    // });

    let select = document.getElementById("themeselect");
	let currentTheme = "vs";
	select.onchange = function () {
		currentTheme = select.options[select.selectedIndex].value;
		monaco.editor.setTheme(currentTheme);
	};
});

function getCode() {
    return [
        "#! lang=hausa",
        "",
        "aiki gayar() {",
        " print('Sannu!');",
        "};",
        "",
        "gayar();"
    ].join("\n");
};

function reset() {
    document.getElementById("output").innerText = "";
            document.getElementById("output").style.borderColor = "initial";
            document.getElementById("python_code").innerText = "!"
}

async function runcode() {

    reset();

    let code = window.editor.getValue();
    let compile_only = document.getElementById("compile_only");

    let req_body = {
        code,
        option: "execute_only",
        compile_only: compile_only.checked,
        save: false
    }


    fetch('api/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify(req_body)
      }).then(async function(response) {
        // ...
        console.log(response);
        if (response.ok) {
            console.log('Code compiled successfully!');
            let res = await response.json();

            console.log(res);

            if (res.status == "error" || res.data.error) {
            document.getElementById("output").innerText = res.data.error;
            document.getElementById("output").style.borderColor = "red";
            document.getElementById("python_code").innerText = "ERROR!";
            } else {
                document.getElementById("output").innerText = res.data.python_result;
                document.getElementById("python_code").innerText = res.data.python_source;
            }
        }else {
            console.log(response);

            document.getElementById("output").innerText = "ERROR!";
            document.getElementById("output").style.borderColor = "red";
            document.getElementById("python_code").innerText = "ERROR!";
        }
    });

}