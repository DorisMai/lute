"""Parameters for T-Jumpt scattering analysis task.

This module contains the parameter model for the T-Jumpt scattering analysis
that processes smalldata h5 files and produces new h5 files with a matplotlib
summary figure for elog display.
"""

from typing import Optional, Dict, Any
from pydantic import Field, validator, root_validator

from lute.io.models.base import ThirdPartyParameters
from lute.io.db import read_latest_db_entry
import os


class ClassifyTJumpParameters(ThirdPartyParameters):
    """Parameters for classification of T-jump task.

    This task classifies tjump pumping based on the scattering data from input
    h5 file, produces output csv file along with a summary plot for elog display.
    """

    class Config(ThirdPartyParameters.Config):
        """Configuration for parameters."""

        long_flags_use_eq: bool = True
        set_result: bool = True
        result_from_params: str = ""

    # ====== BEGIN PENDING KEVIN'S SCRIPTS ======
    executable: str = Field("python", description="Python executable.", flag_type="")
    python_script: str = Field(
        description="Path to the TJump processing script",
        flag_type="",
    )

    input_h5: str = Field(
        "",
        description="Path to input smalldata h5 file that contains 1D Azimuthal Integration data",
        flag_type="--",
        rename_param="input",
    )

    exp: str = Field(
        "",
        description="LCLS experiment identifier",
        flag_type="--",
        rename_param="exp",
    )
    run: int = Field(
        -1,
        description="LCLS run number",
        flag_type="--",
        rename_param="run",
    )

    # Output parameters
    output_dir: str = Field(
        "",
        description="Path to output files, including output h5 file and png files for "
        "intermediate plots",
        flag_type="--",
        rename_param="output",
    )

    output_csv: str = Field(
        "",
        description="name of the output csv file that contains the classification results",
        flag_type="--",
        rename_param="output_csv",
    )

    output_png: str = Field(
        "",
        description="name of the output png file that contains the summary plot",
        flag_type="--",
        rename_param="output_png",
    )

    # any other parameters....

    # ====== END PENDING KEVIN'S SCRIPTS ======
    @validator("exp")
    def validate_exp(cls, exp: str, values: Dict[str, Any]):
        """Validate that the experiment identifier is a valid LCLS experiment identifier."""
        if exp == "":
            exp = values["lute_config"].experiment
        return exp

    @validator("run")
    def validate_run(cls, run: int, values: Dict[str, Any]):
        """Validate that the run number is a valid LCLS run number."""
        if run == -1:
            run = int(values["lute_config"].run)
        return run

    @validator("output_dir")
    def validate_output_dir(cls, output_dir: str, values: Dict[str, Any]):
        """Create output directory if it doesn't exist."""
        if output_dir == "":
            exp: str = values["lute_config"].experiment
            run: int = int(values["lute_config"].run)
            hutch: str = exp[:3]
            output_dir = f"/sdf/data/lcls/ds/{hutch}/{exp}/stats/summary/TJumpClassification/{run:04d}"
        import os

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir

    @validator("input_h5")
    def validate_smd_path_for_run(cls, smd_path: str, values: Dict[str, Any]) -> str:
        if smd_path == "":
            run: int = int(values["lute_config"].run)
            # Try from database first
            hdf5_path: Optional[str] = read_latest_db_entry(
                f"{values['lute_config'].work_dir}",
                "SubmitSMD",
                "result.payload",
                for_run=run,
            )
            if hdf5_path is not None:
                return hdf5_path
            else:
                exp: str = values["lute_config"].experiment
                hutch: str = exp[:3]
                hdf5_path = f"/sdf/data/lcls/ds/{hutch}/{exp}/hdf5/smalldata/{exp}_Run{run:04d}.h5"
                if os.path.exists(hdf5_path):
                    return hdf5_path
                raise ValueError("No path provided for hdf5 and cannot auto-determine!")
        return smd_path

    # ====== BEGIN PENDING KEVIN'S SCRIPTS ======
    @validator("output_csv")
    def validate_output_csv(cls, output_csv: str, values: Dict[str, Any]):
        # if not supplied, create a default name based on the input h5 file
        if output_csv == "":
            run: int = int(values["lute_config"].run)
            output_csv = f"run{run:04d}_tjump_classifier.csv"
        return output_csv

    @validator("output_png")
    def validate_output_png(cls, output_png: str, values: Dict[str, Any]):
        if output_png == "":
            run: int = int(values["lute_config"].run)
            output_png = f"run{run:04d}_tjump_classifier.png"
        return output_png

    # ====== END PENDING KEVIN'S SCRIPTS ======

    @root_validator(pre=False)
    def define_result(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # Extract the values of output_dir and out_name
        output_dir: str = values["output_dir"]
        out_name: str = values["output_h5"]
        result: str = f"{output_dir}/{out_name}"
        cls.Config.result_from_params = result
        return values
