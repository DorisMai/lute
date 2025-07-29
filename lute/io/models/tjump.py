"""Parameters for T-Jumpt scattering analysis task.

This module contains the parameter model for the T-Jumpt scattering analysis
that processes smalldata h5 files and produces new h5 files with a matplotlib
summary figure for elog display.
"""

from typing import Optional, Dict, Any
from pydantic import Field, validator, root_validator

from lute.io.models.base import ThirdPartyParameters
from lute.io.models.validators import validate_smd_path


class TJumpParameters(ThirdPartyParameters):
    """Parameters for TJump analysis task.

    This task processes smalldata h5 files to analyze solvent scattering in
    temperature jump experiments, produces output h5 files along with summary
    plots for elog display.
    """

    class Config(ThirdPartyParameters.Config):
        """Configuration for parameters."""

        long_flags_use_eq: bool = True
        set_result: bool = True
        result_from_params: str = ""

    # ====== BEGIN PENDING ALEX SCRIPTS ======
    executable: str = Field(
        "/path/to/tjump_script.py",
        description="Path to the TJump processing script",
    )

    # Input parameters, auto-retrieve from previous smalldata result if not supplied
    _find_smd_path = validate_smd_path("input_h5")
    input_h5: str = Field(
        "",
        description="Path to input smalldata h5 file that contains 1D Azimuthal Integration data",
        flag_type="--",
        rename_param="input",
    )

    # Output parameters
    output_dir: str = Field(
        "",
        description="Path to output files, including output h5 file and png files for "
        "intermediate plots",
        flag_type="--",
        rename_param="output",
    )

    output_h5: str = Field(
        "",
        description="name of the output h5 file that contains scaled 1D data, time stamp, "
        "evr code, and all individual filtering masks where columns are "
        "boolean and listed in the ordering of applied filters",
        flag_type="--",
        rename_param="output_h5",
    )

    # # Other potential parameters
    # zscore_threshold: Optional[float] = Field(
    #     2,
    #     description="Z-score threshold for filtering",
    #     flag_type="--",
    # )

    # qmin: Optional[float] = Field(
    #     0.3,
    #     description="Minimum q-range for analysis (optional)",
    #     flag_type="--",
    # )

    # qmax: Optional[float] = Field(
    #     3.2,
    #     description="Maximum q-range for analysis (optional)",
    #     flag_type="--",
    # )

    # ====== END PENDING ALEX SCRIPTS ======
    @validator("executable")
    def validate_executable_exists(cls, v):
        """Validate that the executable exists."""
        import os

        if not os.path.exists(v):
            raise ValueError(f"Executable not found: {v}")
        return v

    @validator("output_dir")
    def validate_output_dir(cls, output_dir: str, values: Dict[str, Any]):
        """Create output directory if it doesn't exist."""
        if output_dir == "":
            exp: str = values["lute_config"].experiment
            run: int = int(values["lute_config"].run)
            hutch: str = exp[:3]
            output_dir = f"/sdf/data/lcls/ds/{hutch}/{exp}/stats/summary/TJump"
        import os

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir

    # ====== BEGIN PENDING ALEX SCRIPTS ======
    @validator("output_h5")
    def validate_output_h5(cls, output_h5: str, values: Dict[str, Any]):
        # if not supplied, create a default name based on the input h5 file
        if output_h5 == "":
            output_h5 = "scaled_and_processed.h5"
        return output_h5

    # ====== END PENDING ALEX SCRIPTS ======

    @root_validator(pre=False)
    def define_result(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # Extract the values of output_dir and out_name
        output_dir: str = values["output_dir"]
        out_name: str = values["output_h5"]
        result: str = f"{output_dir}/{out_name}"
        cls.Config.result_from_params = result
        return values
