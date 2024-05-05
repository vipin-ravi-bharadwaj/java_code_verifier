public class StringBuilderAppendException {
    public static void main(String[] args) {
        try {
            // Creating a StringBuilder object
            StringBuilder sb = new StringBuilder(10);

            // Appending a long string to the StringBuilder
            sb.append("This is a long string that exceeds the initial capacity of the StringBuilder.");

            // Printing the StringBuilder content
            System.out.println("StringBuilder content: " + sb.toString());
        } catch (OutOfMemoryError e) {
            // Catching the OutOfMemoryError, which may occur if the StringBuilder's capacity is exceeded
            System.out.println("OutOfMemoryError caught: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
