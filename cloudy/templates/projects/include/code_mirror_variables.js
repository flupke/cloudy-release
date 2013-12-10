$(function()
{
    // Change CodeMirror mode when the variables format select changes
    $('#id_variables_format').change(function()
    {
        var value = $(this).val();
        if (value === 'yaml') {
            variables_editor.setOption('mode', 'yaml');
            variables_editor.setOption('smartIndent', true);
        } else if (value === 'json') {
            variables_editor.setOption('mode',  {name: 'javascript', json: true, statementIndent: 0});
            // Disable smartIndent for JSON because it's broken inside objects
            variables_editor.setOption('smartIndent', false);
        } else if (value === 'python') {
            variables_editor.setOption('mode', 'python');
            variables_editor.setOption('smartIndent', true);
        }
    });

    $('#id_variables_format').change();

    // Convert tab to spaces
    variables_editor.addKeyMap({
        Tab: function(cm) {
            if (cm.getSelection().length) {
                CodeMirror.commands.indentMore(cm);
            } else { 
                cm.replaceSelection("    ", "end");
            }
        }
    });

    $('.CodeMirror').resizable({
        resize: function() {
            variables_editor.setSize($(this).width(), $(this).height());
        }
    });
});
