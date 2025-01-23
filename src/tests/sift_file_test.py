import pytest
from pathlib import Path
import Language.Exceptions.SiftFileExceptions as SFE
import Language.Exceptions.SyntaxExceptions as SYE
from FileOperations.SiftFile import SiftFile
class TestSiftFileConstructor:
    def test_empty_string_path(self):
        with pytest.raises(SFE.ExceptionList) as exc_info:
            obj = SiftFile("", True)
            obj.validate_correct_path_type()
            obj.verify_filepath()
        # Extract the raised exception
            exception_list = exc_info.value.exception_list

            # Verify specific exceptions are present in the ExceptionList
            assert any(isinstance(e, ValueError) and "not a file" in str(e) for e in exception_list), \
                f"Expected a ValueError about 'not a file', but got: {exception_list}"
            assert any(isinstance(e, ValueError) and ".sift extension" in str(e) for e in exception_list), \
                f"Expected a ValueError about '.sift extension', but got: {exception_list}"
        
    def test_none_type_path(self):
        with pytest.raises(SFE.BadArgumentTypeException, match="Expected path of type string or Path, recieved type: <class 'NoneType'>"):
            obj = SiftFile(None, True)
            obj.validate_correct_path_type()
    
    def test_existing_path_bad_extension(self):
        with pytest.raises(SFE.ExceptionList) as exc_info:
            existing_path =Path("src/tests/testsamples/bad_extension.txt")
            obj = SiftFile(existing_path, True)
            obj.verify_filepath()
            exception_list = exc_info.value.exception_list
            assert any(isinstance(e, ValueError) and ".sift extension" in str(e) for e in exception_list), \
                f"Expected a ValueError about '.sift extension', but got: {exception_list}"
            
    def test_non_existent_path(self):
        with pytest.raises(SFE.ExceptionList) as exc_info:
            non_existent_path = Path("src/tests/testsamples/does_not_exist.sift")
            obj = SiftFile(non_existent_path, True)
            obj.verify_filepath()
            exception_list = exc_info.value.exception_list
            assert any(isinstance(e, FileNotFoundError) and "does not exist" in str(e) for e in exception_list), \
                f"Expected a ValueError about 'does not exist', but got: {exception_list}"
    def test_validate_full_construction(self):
        valid_path = Path("src/tests/testsamples/valid.sift")
        obj = SiftFile(valid_path)
        tree = obj.show_tree()
        assert tree is not None, "The high level structure tree is 'None'."
        assert "target_list" in tree, f"Expected 'target_list' field in tree, none was seen. Here's tree: {tree}"
        assert "target_1" in tree, f"Expected 'target_1' in tree, none was seen. Here's tree: {tree}"

class TestGrammarParsingExceptionTypes:
    def test_multiple_target_definitions(self):
        """ TODO
        - Lark reports the line number and the offending text when it parses the grammar in the file
        - Need to make HighLevelGrammar report this exception back to SiftFile somehow who then raises the exception
        - Or, alternatively, HighLevelGrammar raises the exception. 
        """
        
        with pytest.raises(SYE.MultipleTargetsDefinitions) as exc_info:
            SiftFile("src/tests/testsamples/multiple_target_definitions.sift")
        assert exc_info.value.content.get(1, None) is not None, "The bad file had multiple target definitions; \
                                            expected a reported violating line 1, none found in the exception contents."
        assert exc_info.value.content.get(2, None) is not None, "The bad file had multiple target definitions; \
                                expected a reported violating line 2, none found in the exception contents."
    def test_bad_targets_definition(self):
        """ TODO
        - Lark reports the line number and the offending text when it parses the grammar in the file
        - Need to make HighLevelGrammar report this exception back to SiftFile somehow who then raises the exception
        - Or, alternatively, HighLevelGrammar raises the exception. 
        """
        
        with pytest.raises(SYE.IncorrectTargetsDefinition) as exc_info:
            SiftFile("src/tests/testsamples/bad_targets.sift")
        assert exc_info.value.content.get(1, None) is not None, "The bad file had an invalid targets definition; \
                                expected a reported violating line 1, none found in the exception contents."

    def test_bad_variable_definition(self):
        """ TODO
        Current grammar doesn't identify this as bad.
        """
        with pytest.raises(SYE.InvalidCharactersInVariable) as exc_info:
            SiftFile("src/tests/testsamples/invalid_var_characters.sift")
        assert exc_info.value.content.get(1, None) is not None, "The bad file had an invalid variable in the targets definition; \
                                expected a reported violating line 1, none found in the exception contents."
    def test_bad_variable_assignment(self):
        """TODO
        Current grammar doesn't identify this as bad.
        """
        
        with pytest.raises(SYE.IncorrectTargetsDefinition) as exc_info:
            SiftFile("src/tests/testsamples/colon_targets_assignment.sift")
        assert exc_info.value.content.get(1, None) is not None, "The bad file had an invalid assignment in the targets definition (using ':'); \
                                expected a reported violating line 1, none found in the exception contents."
    """ TODO
    Add more cases when these are built out
    """
    
class TestDirectTreeCreation:
    def test_target_node(self):
        obj = SiftFile("src/tests/testsamples/valid1.sift", test_mode=True)
        content = obj._parse_file()
        tree = obj._make_tree(content)
        tree.print_tree()
        target_list = tree.get_all_targets()
        



    
