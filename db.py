from sqlalchemy import create_engine, text, update

DB_NAME = "feedback_db"

connection_string = f'mysql+mysqlconnector://root:root123!@127.0.0.1:3306/{DB_NAME}'
engine = create_engine(connection_string)


def insert_classification_request(input_text, predicted_category):
    with engine.connect() as connection:
        try:
            statement = text("insert into feedback(f_input_text, f_c_predicted_category) values(:f_input_text, :f_c_predicted_category);")
            connection.execute(statement, {'f_input_text': input_text, 'f_c_predicted_category': predicted_category})
            connection.commit()
            prediction_id = connection.execute(text("select last_insert_id()")).fetchone()[0]

            statement_finetune = text(
                "insert into feedback_for_finetune(f_predictionid, f_input_text, f_c_predicted_category) values(:predictionid, :f_input_text, :f_c_predicted_category);")
            connection.execute(statement_finetune, {'f_input_text': input_text, 'f_c_predicted_category': predicted_category, 'predictionid': prediction_id})
            connection.commit()
            return prediction_id
        except:
            return -1


def insert_feedback(predictionid, category):
    try:
        with engine.connect() as connection:
            statement = text("update feedback set f_c_feedback_category = :category where f_id = :predictionid;")
            connection.execute(statement, {"category": category, "predictionid": predictionid})
            connection.commit()

            statement_finetune = text("update feedback_for_finetune set f_c_feedback_category = :category where f_predictionid = :predictionid;")
            connection.execute(statement_finetune, {"category": category, "predictionid": predictionid})
            connection.commit()
            return 200
    except Exception as e:
        print(f"Error inserting feedback: {e}")
        return 500


def get_feedback_for_finetuning():
   try:
        with engine.connect() as connection:
            statement = text("select f_input_text, f_c_feedback_category from feedback_for_finetune;")
            feedback = connection.execute(statement).fetchall()
            return feedback

   except Exception as e:
       print(f"Error get_feedback_for_finetuning: {e}")
       return 500


def get_feedback():
   try:
        with engine.connect() as connection:
            statement = text("select  f_input_text, f_c_predicted_category, f_c_feedback_category from feedback;")
            feedback = connection.execute(statement).fetchall()
            return feedback

   except Exception as e:
       print(f"Error get_feedback: {e}")
       return 500


def log_finetune():
    try:
        with engine.connect() as connection:
            statement= text("insert into finetune_logs(timestamp) value (current_time());")
            connection.execute(statement)
            connection.commit()
            return 200
    except Exception as e:
        print(f"Error log_finetune: {e}")
        return 500

def delete_feedback_finetune():
    try:
        with engine.connect() as connection:
            statement = text("delete from feedback_for_finetune;")
            connection.execute(statement)
            connection.commit()
            return 200
    except Exception as e:
        print(f"Error delete_feedback_finetune: {e}")
        return 500