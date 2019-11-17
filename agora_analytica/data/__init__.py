import pandas as pd


class DataSetInstance(pd.DataFrame):
    @property
    def _constructor(self):
        """ Return subbing class, not dataframe """
        return type(self)

    def linear_answers(self) -> pd.DataFrame:
        """
        All answer which are numeric between ranges.
        """
        raise NotImplementedError()

    def multiselect_answers(self) -> pd.DataFrame:
        """
        Multiselect answers.
        """
        raise NotImplementedError()

    def text_answers(self) -> pd.DataFrame:
        """
        Free text answers.
        """
        raise NotImplementedError()
