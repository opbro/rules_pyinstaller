
""" Rules for building binaries using pyinstaller"""



def _pyinstaller_build_impl(ctx):
    wheel_dependancy = depset(
        direct = ctx.files.deps,
    )
    if not ctx.attr.executable_name:
        executable_name = ctx.attr.name + ".exe"
    outfile = ctx.actions.declare_file(executable_name)
    main_file = ctx.file.main
    print(main_file)
    print(executable_name)
    print(ctx.files.deps)

    args = ctx.actions.args()
    args.add_all(wheel_dependancy, format_each="--wheel=%s")
    args.add("--outfile", outfile.path)
    args.add("--main", main_file.path)
    args.add("--pyinstallerpath", ctx.attr.pyinstaller_path)
    ctx.actions.run(
        inputs = depset(transitive = [wheel_dependancy, depset(direct=[main_file])]),
        outputs = [outfile],
        arguments = [args],
        executable = ctx.executable._pyinstaller,
        progress_message = "Building executable",
    )

    return [
        DefaultInfo(
            files = depset([outfile]),
            data_runfiles = ctx.runfiles(files = [outfile]),
        )
    ]



pyinstaller_build = rule(
    implementation = _pyinstaller_build_impl,
    doc = """
    This will take python whl's and a main python script to build an executable from.
    """,
    attrs = {
        "deps": attr.label_list(
            doc = """
            This should be the py_wheel outputs
            """
        ),
        "main": attr.label(
            mandatory = True,
            allow_single_file = True,
        ),
        "executable_name": attr.string(default=""),
        "pyinstaller_path": attr.string(default="C:\\Users\\kkubis\\AppData\\Local\\Programs\\Python\\Python37\\Scripts\\pyinstaller.exe"),
        "_pyinstaller": attr.label(
            executable = True,
            cfg = "host",
            default = "//pyinstaller_runner:pyinstaller_runner"
        )
    },
)
