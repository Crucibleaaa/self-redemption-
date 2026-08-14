import Lake
open Lake DSL

package BasepointSelfRef

def pkgDir := "/home/ethanw/llm-research/src/relative-recursion/formal/.lake/packages"

require mathlib from pkgDir ++ "/mathlib"
require aesop from pkgDir ++ "/aesop"
require batteries from pkgDir ++ "/batteries"
require Qq from pkgDir ++ "/Qq"
require proofwidgets from pkgDir ++ "/proofwidgets"
require LeanSearchClient from pkgDir ++ "/LeanSearchClient"
require importGraph from pkgDir ++ "/importGraph"
require Cli from pkgDir ++ "/Cli"
require plausible from pkgDir ++ "/plausible"

lean_lib BasepointSelfRef
