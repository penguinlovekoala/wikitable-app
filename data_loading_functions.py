class TEXTLoader:
    def __init__(self, dir_):
        self.dir_ = dir_
        self.data = self._load(dir_=dir_)

    def __call__(self):
        return self.data

    def _load(self, dir_):
        import codecs
        f_ = codecs.open(dir_, encoding="utf-8")
        str_ = f_.read()
        f_.close()
        return str_

    def get_line_list(self):
        return [line.strip() for line in self.data.split("\n") if line]


class CSVLoader(TEXTLoader):
    def _load(self, dir_):
        import csv
        data_list = []
        with open(self.dir_, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data_list.append(row)
        return data_list


class TEXTSaver:
    def __init__(self, data_, dir_, tail_=None):
        self.data_ = data_
        if tail_:
            self.dir_ = self.add_tail(dir_, tail_)
        else:
            self.dir_ = dir_
        self.loader_class = TEXTLoader

    def __call__(self):
        if isinstance(self.data_, str):
            self._backup_original_file_if_override(dir_=self.dir_)
            self._save(data_=self.data_, dir_=self.dir_)
        else:
            raise TypeError("the text saving is not yet implemented for the type that is not str.")

    def _save(self, data_, dir_):
        import codecs
        f_ = codecs.open(dir_, mode='w', encoding='utf8')
        print(data_.strip(), file=f_)
        f_.close()

    def _backup_original_file_if_override(self, dir_):
        """
        before save a file, backup the file, after checking
        whether there is already a file with the same file name,
        in other words, this function backup the original file
        if the function is attempting to override it.
        :param dir_: the dir to check
        :return: None
        """
        import os
        if os.path.isfile(dir_):
            loader = self.loader_class(dir_)
            data_to_backup = loader()
            tail_index, loop_count, limit_loop_count = 0, 0, 100
            while True:
                tail_index += 1
                loop_count += 1
                if loop_count > limit_loop_count:
                    break
                backup_dir = self.add_tail(dir_=dir_,
                                           tail_=f".{tail_index}.")
                if os.path.isfile(backup_dir):
                    pass
                else:
                    break
            self._save(
                dir_=backup_dir,
                data_=data_to_backup
            )

    @staticmethod
    def add_tail(dir_, tail_):
        dir_front, suffix = ".".join(dir_.split(".")[:-1]), dir_.split(".")[-1]
        dir_ = dir_front + tail_ + suffix
        return dir_


class JSONSaver(TEXTSaver):
    def __init__(self, data_, dir_, tail_=None):
        super().__init__(data_, dir_, tail_=tail_)
        self.loader_class = JSONLoader

    def __call__(self):
        if isinstance(self.data_, list) or isinstance(self.data_, dict):
            self._backup_original_file_if_override(dir_=self.dir_)
            self._save(data_=self.data_, dir_=self.dir_)
        else:
            raise TypeError("the json saving is not yet implemented for the type that is neither list nor dict.")

    def _save(self, data_, dir_):
        import json
        with open(dir_, 'w') as f_:
            json.dump(data_, f_,
                      indent=4, sort_keys=False, ensure_ascii=False)
        return 1


class JSONLoader(TEXTLoader):
    def _load(self, dir_):
        """
        :param dir_: the dir of the json file
        :return:
        """
        import json
        with open(dir_) as json_file:
            loaded_obj = json.load(json_file)
        if isinstance(loaded_obj, dict):
            return loaded_obj
        assert isinstance(loaded_obj, list), (
            f"the type of the loaded object from json should be list if it is not a dict, but it is {type(loaded_obj)}."
        )
        if len(loaded_obj) == 1:
            loaded_obj = loaded_obj[0]
            assert isinstance(loaded_obj, dict), (
                f"the type should be dict if the len of the object is 1, but it is {type(loaded_obj)}."
            )
        return loaded_obj

