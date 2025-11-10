# verifier/runners/java_runner.py
from __future__ import annotations
from pathlib import Path
from verifier.sandbox import mkworkdir, write_file, run_cmd, cleanup, RunResult

TRANSLATED_TEMPLATE = """\
// GENERATED
public class Translated {{
{user_code}
}}
"""

MAIN_TEMPLATE = """\
// GENERATED
public class Main {{
    public static void main(String[] args) {{
        int[] a = new int[args.length];
        for (int i = 0; i < args.length; i++) a[i] = Integer.parseInt(args[i]);
        int out;
        switch(a.length){{
            case 0: out = Translated.{func_name}(); break;
            case 1: out = Translated.{func_name}(a[0]); break;
            case 2: out = Translated.{func_name}(a[0],a[1]); break;
            case 3: out = Translated.{func_name}(a[0],a[1],a[2]); break;
            case 4: out = Translated.{func_name}(a[0],a[1],a[2],a[3]); break;
            default: throw new RuntimeException("Too many args");
        }}
        System.out.println(out);
    }}
}}
"""

def run_java_func(code: str, func_name: str, args: list[int]) -> RunResult:
    """
    'code' must contain a compatible static method (returns int).
    Example: public static int gcd(int a, int b) { ... }
    """
    work = mkworkdir("ct_java_")
    try:
        translated = TRANSLATED_TEMPLATE.format(user_code=code)
        main = MAIN_TEMPLATE.format(func_name=func_name)

        write_file(work / "Translated.java", translated)
        write_file(work / "Main.java", main)

        c = run_cmd(["javac", "Translated.java", "Main.java"], cwd=work)
        if not c.ok:
            return c
        r = run_cmd(["java", "Main", *map(str, args)], cwd=work)
        return r
    finally:
        cleanup(work)
