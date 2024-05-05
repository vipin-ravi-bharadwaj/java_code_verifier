public class CastExceptionExampleJava8 {
    public static void main(String[] args) {
        try {
            // Creating an Object array with some String and Integer objects
            Object[] objArray = new Object[]{"Hello", "World", 123, 456};

            // Attempting to cast each element of the array to String
            for (Object obj : objArray) {
                String str = (String) obj; // This line will throw ClassCastException for the Integer objects
                System.out.println("Casting successful: " + str);
            }
        } catch (ClassCastException e) {
            // Catching the ClassCastException
            System.out.println("ClassCastException caught: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
